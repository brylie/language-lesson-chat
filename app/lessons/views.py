import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import TranscriptMessage

TTS_MODEL = "tts-1"


class OpenAITTSVoices:
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"


@csrf_exempt
@login_required
def generate_audio(request, message_id):
    try:
        message = TranscriptMessage.objects.get(id=message_id)

        # Ensure the request user is the owner of the message
        if message.transcript.user != request.user:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        text = message.content
        voice = message.transcript.lesson.voice

        # Check if the audio file already exists
        speech_file_path = f"speech_{message_id}.mp3"

        if default_storage.exists(speech_file_path):
            return JsonResponse({"audio_url": default_storage.url(speech_file_path)})

        # Map the lesson voice to the LLM model voice
        llm_voice = map_lesson_voice_to_llm_voice(voice)

        # Call OpenAI text-to-speech API
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.audio.create(model=TTS_MODEL, input=text, voice=llm_voice)

        # Save the audio to a temporary file
        speech_file_path = default_storage.save(
            speech_file_path, ContentFile(response.content)
        )

        return JsonResponse({"audio_url": default_storage.url(speech_file_path)})

    except TranscriptMessage.DoesNotExist:
        return JsonResponse({"error": "Message not found"}, status=404)
    except Exception as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=500)


def map_lesson_voice_to_llm_voice(lesson_voice):
    if lesson_voice == "male":
        return OpenAITTSVoices.ONYX
    elif lesson_voice == "female":
        return OpenAITTSVoices.NOVA
    else:
        return OpenAITTSVoices.ALLOY  # Default to Alloy for a gender-neutral default
