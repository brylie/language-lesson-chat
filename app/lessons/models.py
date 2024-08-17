from django.db import models
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
import os
from openai import OpenAI
import logging
from pydantic import BaseModel, Field, ValidationError
from typing import List
from django_htmx.http import HttpResponseClientRedirect

# Set up logging
logger = logging.getLogger(__name__)

# Define the character limit constant
MAX_USER_MESSAGE_LENGTH = 100

# Define the constant for responses without a key concept
NO_KEY_CONCEPT = "NO_KEY_CONCEPT"


class Suggestion(BaseModel):
    """
    Represents a suggestion for the user to consider in response to a chat message.

    Attributes:
        text (str): The text of the suggestion.
    """

    text: str


class ChatResponse(BaseModel):
    """
    Represents a response from a chat assistant, including the assistant's message,
    a list of suggestions, and the key concept addressed in the response.

    Attributes:
        assistant_message (str): The message generated by the chat assistant.
        suggestions (List[Suggestion]): A list of suggestions related to the chat response.
        addressed_key_concept (str): The single key concept addressed in this response,
            or 'NO_KEY_CONCEPT' if none was used.
    """

    assistant_message: str
    suggestions: List[Suggestion]
    addressed_key_concept: str = Field(
        ...,
        description=f"The single key concept addressed in this response, or '{NO_KEY_CONCEPT}' if none was used",
    )


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
        help_text="Specify the target language for this lesson (e.g., 'English', 'Spanish', 'French'). This will help the AI assistant provide appropriate responses and suggestions.",
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ("a1", "A1 - Beginner"),
            ("a2", "A2 - Elementary"),
            ("b1", "B1 - Intermediate"),
            ("b2", "B2 - Upper Intermediate"),
            ("c1", "C1 - Advanced"),
            ("c2", "C2 - Proficiency"),
        ],
        default="a1",
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
        FieldPanel("difficulty_level"),
        FieldPanel("estimated_time"),
        FieldPanel("llm_system_prompt"),
        InlinePanel("key_concepts", label="Key Concepts"),
    ]

    def get_context(self, request: HttpRequest) -> dict:
        """
        Generate and return the context dictionary for the lesson page.

        This method extends the default context with additional information
        specific to the lesson, such as key concepts and a language model (LLM)
        prompt.

        :param request: The HTTP request object.
        :return: A dictionary containing the context for rendering the lesson page.

        The context includes:
        - key_concepts: A queryset of all key concepts associated with the lesson.
        - max_message_length: The maximum allowed length for user messages.
        - llm_prompt: A rendered string template that serves as a prompt for the
            language model, incorporating lesson-specific details such as difficulty
            level, location, system prompt, key concepts, conversation history, and
            language.
        """
        context = super().get_context(request)
        context["key_concepts"] = self.key_concepts.all()
        context["max_message_length"] = MAX_USER_MESSAGE_LENGTH

        # Generate the LLM prompt
        prompt_context = {
            "difficulty_level": self.get_difficulty_level_display(),
            "location": self.location,
            "system_prompt": self.llm_system_prompt,
            "key_concepts": [concept.concept for concept in self.key_concepts.all()],
            "conversation_history": request.session.get("conversation_history", []),
            "language": self.language,
        }
        context["llm_prompt"] = render_to_string(
            "lessons/prompt_template.txt", prompt_context
        )

        return context

    def serve(self, request: HttpRequest) -> HttpResponse:
        """
        Handles HTTP requests for the Lesson page, processing user interactions
        and managing conversation state.

        This method processes POST requests to handle user messages and reset
        conversation history. It validates user input, interacts with the language
        model to generate responses, and updates the session state accordingly.

        Parameters:
            request (HttpRequest): The HTTP request object containing metadata
            about the request.

        Returns:
            HttpResponse: The response object containing the rendered HTML content
            or JSON response based on the request type and processing outcome.
        """

        if request.method == "GET" and "success" in request.GET:
            return self.render_success_if_complete_else_redirect_to_self(request)

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

            llm_response = self.get_llm_response(request, user_message)

            lesson_is_complete = self.user_has_responded_to_all_key_concepts(request)
            if lesson_is_complete:
                return self.handle_lesson_completion(request)

            return HttpResponse(llm_response)

        return super().serve(request)

    def handle_lesson_completion(self, request: HttpRequest) -> HttpResponse:
        return HttpResponseClientRedirect(f"{self.url}?success=true")

    def render_success_if_complete_else_redirect_to_self(
        self, request: HttpRequest
    ) -> HttpResponse:
        """Ensure the student has responded to all key concepts before rendering the success page.

        If the student has not responded to all key concepts, redirect back to the lesson page."""
        if self.user_has_responded_to_all_key_concepts(request):
            self.reset_lesson_progress(request)
            return self.render_success_page(request)
        else:
            return HttpResponseClientRedirect(self.url)

    def handle_start_over(self, request: HttpRequest) -> HttpResponse:
        self.reset_lesson_progress(request)

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

    def render_success_page(self, request: HttpRequest) -> HttpResponse:
        context = self.get_context(request)
        context.update(
            {
                "key_concepts": self.key_concepts.all(),
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
        """
        Generates a response from a language model based on the user's message and the lesson context.

        This method constructs a prompt using the lesson's context and the user's message, sends it to
        the language model, and processes the response. It updates the conversation history and addressed
        key concepts in the session, and returns an HTTP response with the assistant's message and suggestions.

        :param request: The HTTP request object containing session data.
        :param user_message: The message input by the user.
        :return: An HTTP response containing the assistant's message and suggestions.

        :raises ValidationError: If there is an error in validating the response data.
        :raises Exception: For any unexpected errors during the process.
        """

        conversation_history = request.session.get("conversation_history", [])

        addressed_key_concepts = request.session.get("addressed_key_concepts", [])
        prompt = self.get_context(request)["llm_prompt"]
        messages = (
            [
                {"role": "system", "content": prompt},
            ]
            + conversation_history
            + [{"role": "user", "content": user_message}]
        )

        try:
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=messages,
                response_format=ChatResponse,
            )

            chat_response = completion.choices[0].message

            if chat_response.refusal:
                logger.warning(f"OpenAI API refusal: {chat_response.refusal}")
                return HttpResponse(
                    render_to_string(
                        "lessons/combined_htmx_response.html",
                        {
                            "error": "I'm sorry, but I can't respond to that request. Please try a different question or topic."
                        },
                    )
                )

            response_data = chat_response.parsed

            # Get valid key concepts
            valid_key_concepts = [
                concept.concept for concept in self.key_concepts.all()
            ]

            # Validate key concept
            if response_data.addressed_key_concept not in valid_key_concepts:
                logger.warning(
                    f"Invalid key concept: {response_data.addressed_key_concept}"
                )
                response_data.addressed_key_concept = NO_KEY_CONCEPT
            elif (
                response_data.addressed_key_concept != NO_KEY_CONCEPT
                and response_data.addressed_key_concept not in addressed_key_concepts
            ):
                addressed_key_concepts.append(response_data.addressed_key_concept)

            # Update conversation history
            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append(
                {"role": "assistant", "content": response_data.assistant_message}
            )
            # Limit to last 10 messages
            conversation_history = conversation_history[-10:]

            # Update session variables
            request.session["conversation_history"] = conversation_history
            request.session["addressed_key_concepts"] = addressed_key_concepts

            # Render the combined response
            combined_response = render_to_string(
                "lessons/combined_htmx_response.html",
                {
                    "page": self,
                    "assistant_message": response_data.assistant_message,
                    "suggestions": response_data.suggestions,
                    "addressed_key_concept": response_data.addressed_key_concept,
                    "addressed_key_concepts": addressed_key_concepts,
                    "valid_key_concepts": valid_key_concepts,
                    "no_key_concept": NO_KEY_CONCEPT,
                },
            )

            return HttpResponse(combined_response)

        except ValidationError as e:
            logger.error(f"Validation error in get_llm_response: {str(e)}")
            return HttpResponse(
                render_to_string(
                    "lessons/combined_htmx_response.html",
                    {
                        "error": "An error occurred while processing the response. Please try again."
                    },
                )
            )
        except Exception as e:
            logger.error(f"Unexpected error in get_llm_response: {str(e)}")
            return HttpResponse(
                render_to_string(
                    "lessons/combined_htmx_response.html",
                    {
                        "error": "An unexpected error occurred. Please try again later or contact support if the problem persists."
                    },
                )
            )

    class Meta:
        verbose_name = "Language Lesson"
        verbose_name_plural = "Language Lessons"
