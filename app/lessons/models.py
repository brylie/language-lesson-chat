from django.db import models
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
import logging
from django_htmx.http import HttpResponseClientRedirect
from django.contrib.auth import get_user_model

from .choices import CEFRLevel, VoiceChoice, LanguageChoice
from transcripts.models import Transcript, TranscriptMessage

from .llm import NO_KEY_CONCEPT, get_llm_response

# Set up logging
logger = logging.getLogger(__name__)

# Define the character limit constant
MAX_USER_MESSAGE_LENGTH = 100

# Define the constant for responses without a key concept
SUCCESS_PARAM = "success"
START_OVER_PARAM = "start_over"

User = get_user_model()


class KeyConcept(models.Model):
    lesson = ParentalKey(
        "Lesson", related_name="key_concepts", on_delete=models.CASCADE
    )
    concept = models.CharField(
        max_length=255,
        help_text="Enter a key language concept or vocabulary item for this lesson.",
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Choose an image that represents the key concept. This will help the student visualize the concept.",
    )

    panels = [
        FieldPanel("concept"),
        FieldPanel("image"),
    ]

    def __str__(self):
        return self.concept


class Lesson(Page, ClusterableModel):
    intro = RichTextField(
        blank=True,
        help_text="Provide a brief introduction to the lesson. This will be shown to the student before they start the interactive dialogue.",
    )
    cover_photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Choose an image that represents the setting or theme of the lesson. This will help set the scene for the student.",
    )
    location = models.CharField(
        max_length=100,
        help_text="Specify the location or setting for this lesson (e.g., 'Coffee Shop', 'Airport', 'Art Gallery'). This will be used to set the context for the AI dialogue.",
    )
    language = models.CharField(
        max_length=100,
        choices=LanguageChoice.choices,
        help_text="Specify the target language for this lesson (e.g., 'English', 'Spanish', 'French'). This will help the AI assistant provide appropriate responses and suggestions.",
    )
    voice = models.CharField(
        max_length=20,
        choices=VoiceChoice.choices,
        default=VoiceChoice.MALE,
        help_text="Select the voice for the text-to-speech playback. This will help tailor the audio experience to the student's preference.",
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=CEFRLevel.choices,
        default=CEFRLevel.A1,
        help_text="Select the CEFR level for this lesson. This will help tailor the AI's language complexity to the student's proficiency.",
    )
    estimated_time = models.PositiveIntegerField(
        default=30,
        help_text="Estimate the time (in minutes) it will take to complete this lesson, including the interactive dialogue.",
    )
    llm_system_prompt = models.TextField(
        verbose_name="LLM System Prompt",
        help_text="Provide specific instructions for the AI assistant's behavior in this lesson. For example, 'You are a friendly barista in a busy coffee shop. Engage the student in small talk and help them order a drink.'",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("cover_photo"),
        FieldPanel("location"),
        FieldPanel("language"),
        FieldPanel("voice"),
        FieldPanel("difficulty_level"),
        FieldPanel("estimated_time"),
        FieldPanel("llm_system_prompt"),
        InlinePanel("key_concepts", label="Key Concepts"),
    ]

    def get_context(self, request: HttpRequest) -> dict:
        context = super().get_context(request)
        context["key_concepts"] = self.key_concepts.all()
        context["max_message_length"] = MAX_USER_MESSAGE_LENGTH
        context["transcript"] = self.get_or_create_transcript(request)

        return context

    def serve(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET" and SUCCESS_PARAM in request.GET:
            if self.user_has_responded_to_all_key_concepts(request):
                self.reset_lesson_progress(request)
                return self.render_success_page(request)
            else:
                # If the user has not completed the lesson, reset the progress
                self.reset_lesson_progress(request)

                return redirect(f"{request.path}")

        if request.method == "POST":
            if "start_over" in request.POST:
                return self.handle_start_over(request)

            user_message = request.POST.get("user_message", "")
            response_key_concept = request.POST.get("response_key_concept", "")

            # Server-side validation of message length
            if len(user_message) > MAX_USER_MESSAGE_LENGTH:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"Message exceeds maximum length of {MAX_USER_MESSAGE_LENGTH} characters.",
                    },
                    status=400,
                )

            # Update responded key concepts
            self.update_responded_key_concepts(request, response_key_concept)

            # Log user message
            self.log_message(
                request,
                "user",
                user_message,
                response_key_concept,
            )

            llm_response = self.get_llm_response(request, user_message)

            lesson_is_complete = self.user_has_responded_to_all_key_concepts(request)
            if lesson_is_complete:
                return self.handle_lesson_completion(request)

            return HttpResponse(llm_response)

        return super().serve(request)

    def handle_lesson_completion(self, request: HttpRequest) -> HttpResponse:
        return HttpResponseClientRedirect(f"{self.url}?{SUCCESS_PARAM}=true")

    def render_success_if_complete_else_redirect_to_self(
        self, request: HttpRequest
    ) -> HttpResponse:
        """Ensure the student has responded to all key concepts before rendering the success page.

        If the student has not responded to all key concepts, redirect back to the lesson page."""
        if self.user_has_responded_to_all_key_concepts(request):
            self.reset_lesson_progress(request)
            return self.render_success_page(request)
        else:
            # return HttpResponseClientRedirect(self.url)
            pass

    def handle_start_over(self, request: HttpRequest) -> HttpResponse:
        # Reset lesson progress
        self.reset_lesson_progress(request)

        # Create a new transcript
        new_transcript = self.manage_transcript(request, create_new=True)

        context = self.get_context(request)
        context.update(
            {
                "page": self,
                "assistant_message": "The lesson has been reset. You can start a new dialogue now.",
                "suggestions": [],
                "addressed_key_concept": "",
                "addressed_key_concepts": [],
                "responded_key_concepts": [],
                "no_key_concept": NO_KEY_CONCEPT,
                "transcript_id": new_transcript.id,
            }
        )
        reset_response = render_to_string(
            "lessons/combined_htmx_response.html", context
        )
        return HttpResponse(reset_response)

    def reset_lesson_progress(self, request: HttpRequest):
        request.session["conversation_history"] = []
        request.session["addressed_key_concepts"] = []
        request.session["responded_key_concepts"] = []

    def manage_transcript(
        self,
        request: HttpRequest,
        create_new: bool = False,
    ) -> Transcript:
        if create_new or "transcript_id" not in request.session:
            # Clear existing transcript ID if present
            if "transcript_id" in request.session:
                del request.session["transcript_id"]

            # Create a new transcript
            transcript = Transcript.objects.create(user=request.user, lesson=self)
            request.session["transcript_id"] = transcript.id
        else:
            transcript_id = request.session.get("transcript_id")
            try:
                transcript = Transcript.objects.get(id=transcript_id)
            except Transcript.DoesNotExist:
                # If the transcript doesn't exist, create a new one
                transcript = Transcript.objects.create(user=request.user, lesson=self)
                request.session["transcript_id"] = transcript.id

        return transcript

    def render_success_page(self, request: HttpRequest) -> HttpResponse:
        context = self.get_context(request)

        # Retrieve the current transcript
        transcript = self.manage_transcript(request)
        context["transcript"] = transcript

        # Clear the transcript ID from the session to ensure a new one is created next time
        if "transcript_id" in request.session:
            del request.session["transcript_id"]

        context.update(
            {
                "key_concepts": self.key_concepts.all(),
                "no_key_concept": NO_KEY_CONCEPT,
            }
        )
        return render(request, "lessons/lesson_success.html", context)

    def update_responded_key_concepts(
        self,
        request: HttpRequest,
        response_key_concept: str,
    ):
        """
        Update the list of key concepts that the user has responded to.
        """
        responded_key_concepts = request.session.get("responded_key_concepts", [])
        if (
            response_key_concept
            and response_key_concept != NO_KEY_CONCEPT
            and response_key_concept not in responded_key_concepts
        ):
            responded_key_concepts.append(response_key_concept)
            request.session["responded_key_concepts"] = responded_key_concepts

    def user_has_responded_to_all_key_concepts(self, request: HttpRequest) -> bool:
        """
        Check if the user has responded to all key concepts in the lesson.
        """
        lesson_key_concepts = [concept.concept for concept in self.key_concepts.all()]
        responded_key_concepts = request.session.get("responded_key_concepts", [])
        return set(lesson_key_concepts) == set(responded_key_concepts)

    def get_llm_response(self, request: HttpRequest, user_message: str) -> HttpResponse:
        return get_llm_response(request, user_message, self)

    def log_message(self, request, role, content, key_concept=None, llm_model=None):
        transcript_id = request.session.get("transcript_id")
        if transcript_id:
            TranscriptMessage.objects.create(
                transcript_id=transcript_id,
                role=role,
                content=content,
                key_concept=key_concept if key_concept != NO_KEY_CONCEPT else None,
                llm_model=llm_model if role == "assistant" else None,
            )

    def get_or_create_transcript(self, request: HttpRequest) -> Transcript:
        if "transcript_id" not in request.session:
            transcript = Transcript.objects.create(user=request.user, lesson=self)
        else:
            transcript_id = request.session.get("transcript_id")
            if transcript_id:
                try:
                    transcript = Transcript.objects.get(id=transcript_id)
                except Transcript.DoesNotExist:
                    transcript = Transcript.objects.create(
                        user=request.user, lesson=self
                    )
        request.session["transcript_id"] = transcript.id
        return transcript

    class Meta:
        verbose_name = "Language Lesson"
        verbose_name_plural = "Language Lessons"
        db_table = "lessons"
