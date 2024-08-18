import os
from openai import OpenAI
import logging
from pydantic import BaseModel, Field, ValidationError
from typing import TYPE_CHECKING, List
from django.template.loader import render_to_string
from django.http import HttpResponse

logger = logging.getLogger(__name__)

LLM_MODEL = "gpt-4o-2024-08-06"
NO_KEY_CONCEPT = "NO_KEY_CONCEPT"

if TYPE_CHECKING:
    from .models import Lesson


class Suggestion(BaseModel):
    text: str


class ChatResponse(BaseModel):
    assistant_message: str
    suggestions: List[Suggestion]
    addressed_key_concept: str = Field(
        ...,
        description=f"The single key concept addressed in this response, or '{NO_KEY_CONCEPT}' if none was used",
    )


def render_llm_prompt(lesson: "Lesson", conversation_history: List[dict]):
    prompt_context = {
        "difficulty_level": lesson.get_difficulty_level_display(),
        "language": lesson.language,
        "location": lesson.location,
        "system_prompt": lesson.llm_system_prompt,
        "key_concepts": [concept.concept for concept in lesson.key_concepts.all()],
        "conversation_history": conversation_history,
    }
    return render_to_string("lessons/prompt_template.txt", prompt_context)


def get_llm_response(request, user_message, lesson):
    conversation_history = request.session.get("conversation_history", [])
    addressed_key_concepts = request.session.get("addressed_key_concepts", [])

    prompt = render_llm_prompt(
        lesson=lesson,
        conversation_history=conversation_history,
    )

    messages = (
        [{"role": "system", "content": prompt}]
        + conversation_history
        + [{"role": "user", "content": user_message}]
    )

    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        completion = client.beta.chat.completions.parse(
            model=LLM_MODEL,
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
        valid_key_concepts = [concept.concept for concept in lesson.key_concepts.all()]

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

        # Log assistant message
        lesson.log_message(
            request,
            "assistant",
            response_data.assistant_message,
            response_data.addressed_key_concept,
            LLM_MODEL,
        )

        # Render the combined response
        combined_response = render_to_string(
            "lessons/combined_htmx_response.html",
            {
                "page": lesson,
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
