import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django_htmx.http import HttpResponseClientRedirect
from minigames.blocks import IframeBlock, StepOrderGameBlock
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from transcripts.models import Transcript, TranscriptMessage
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page

from .choices import CEFRLevel, LanguageChoice, VoiceChoice
from .llm import NO_KEY_CONCEPT, get_llm_response

# Set up logging
logger = logging.getLogger(__name__)

# Define the character limit constant
MAX_USER_MESSAGE_LENGTH = 100

# Define the constant for responses without a key concept
CHAT_SUMMARY_PARAM = "chat_summary"
START_OVER_PARAM = "start_over"
MINIGAME_PARAM = "minigame"

User = get_user_model()


class KeyConcept(Orderable):
    lesson = ParentalKey(
        "ChatLesson",
        related_name="key_concepts",
        on_delete=models.CASCADE,
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

    class Meta:
        ordering = ["sort_order"]


class ChatLesson(Page, ClusterableModel):
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
    minigames = StreamField(
        [
            ("step_order_game", StepOrderGameBlock()),
            ("iframe", IframeBlock()),
        ],
        blank=True,
        use_json_field=True,
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
        InlinePanel(
            "key_concepts",
            label="Key Concepts",
            max_num=5,
        ),
        FieldPanel("minigames"),
    ]

    class Meta:
        verbose_name = "Chat Lesson"
        verbose_name_plural = "Chat Lessons"
        db_table = "chat_lessons"

    def get_context(self, request: HttpRequest) -> dict:
        context = super().get_context(request)
        context["key_concepts"] = self.key_concepts.all().order_by("sort_order")
        context["max_message_length"] = MAX_USER_MESSAGE_LENGTH
        context["transcript"] = self.get_or_create_transcript(request)
        context["start_over_param"] = START_OVER_PARAM

        return context

    @method_decorator(login_required)
    def serve(self, request: HttpRequest) -> HttpResponse:
        # Since these parameters are not mutually exclusive,
        # the order of the checks matters.
        # In recent versions of Python, the order of items in a dictionary is guaranteed
        # to be the same as the order they were inserted.
        get_param_handlers = {
            CHAT_SUMMARY_PARAM: self.render_summary_page,
            MINIGAME_PARAM: self.render_minigame,
            START_OVER_PARAM: self.handle_start_over,
        }

        for param, handler in get_param_handlers.items():
            if param in request.GET:
                return handler(request)

        if request.method == "POST":
            return self.handle_chat_message(request)

        return super().serve(request)

    def handle_chat_message(self, request: HttpRequest) -> HttpResponse:
        """
        Handle the user's chat message and return the AI assistant's response.

        If the user has responded to all key concepts, the lesson is considered complete."""
        user_message = request.POST.get("user_message", "")
        response_key_concept = request.POST.get("response_key_concept", "")

        # Validate the message length to prevent abuse
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

        # Check if the lesson is complete
        lesson_is_complete = self.user_has_responded_to_all_key_concepts(request)
        if lesson_is_complete:
            return self.handle_lesson_completion(request)

        # If lesson is not complete, get the LLM response
        llm_response = self.get_llm_response(request, user_message)

        return HttpResponse(llm_response)

    def handle_lesson_completion(self, request: HttpRequest) -> HttpResponse:
        return HttpResponseClientRedirect(f"{self.url}?{CHAT_SUMMARY_PARAM}=true")

    def handle_start_over(self, request: HttpRequest) -> HttpResponse:
        # Reset lesson progress
        self.reset_lesson_progress(request)

        # Create a new transcript
        new_transcript = self.get_or_create_transcript(request, force_create_new=True)

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

        return render(request, "lessons/chat_lesson.html", context)

    def reset_lesson_progress(self, request: HttpRequest) -> None:
        request.session["conversation_history"] = []
        request.session["addressed_key_concepts"] = []
        request.session["responded_key_concepts"] = []

    def render_summary_page(self, request: HttpRequest) -> HttpResponse:
        context = self.get_context(request)

        # Retrieve the current transcript
        transcript = self.get_or_create_transcript(request)
        context["transcript"] = transcript

        context.update(
            {
                "key_concepts": self.key_concepts.all(),
                "no_key_concept": NO_KEY_CONCEPT,
                "start_over_param": START_OVER_PARAM,
                "minigame_param": MINIGAME_PARAM,
            }
        )
        return render(request, "lessons/chat_summary.html", context)

    def render_minigame(self, request: HttpRequest) -> HttpResponse:
        # Convert to 0-based index
        adjusted_minigame_index = int(request.GET.get(MINIGAME_PARAM, 0)) - 1
        if 0 <= adjusted_minigame_index < len(self.minigames):
            minigame = self.minigames[adjusted_minigame_index]
            context = self.get_context(request)
            context.update(
                {
                    "minigame": minigame,
                }
            )
            return render(request, "minigames/minigame.html", context)
        else:
            raise Http404("Minigame not found")

    def update_responded_key_concepts(
        self,
        request: HttpRequest,
        response_key_concept: str,
    ) -> None:
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

    def get_or_create_transcript(
        self,
        request: HttpRequest,
        force_create_new: bool = False,
    ) -> Transcript:
        if force_create_new or "transcript_id" not in request.session:
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
