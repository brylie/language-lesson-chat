from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import openai
import os
from pathlib import Path
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import TranscriptMessage

# Create your views here.

TTS_MODEL = "tts-1"

class OpenAITTSVoices:
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"

@require_POST
@csrf_exempt
def generate_audio(request, message_id):
    try:
        message = TranscriptMessage.objects.get(id=message_id)
        text = message.content
        voice = message.transcript.lesson.voice

        # Map the lesson voice to the LLM model voice
        llm_voice = map_lesson_voice_to_llm_voice(voice)

        # Check if the audio file already exists
        speech_file_path = f"speech_{message_id}.mp3"
        if default_storage.exists(speech_file_path):
            return JsonResponse({'audio_url': default_storage.url(speech_file_path)})

        # Call OpenAI text-to-speech API
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.Audio.create(
            model=TTS_MODEL,
            input=text,
            voice=llm_voice,
        )

        # Save the audio to a temporary file
        speech_file_path = default_storage.save(speech_file_path, ContentFile(response.content))

        return JsonResponse({'audio_url': default_storage.url(speech_file_path)})

    except TranscriptMessage.DoesNotExist:
        return JsonResponse({'error': 'Message not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def map_lesson_voice_to_llm_voice(lesson_voice):
    if lesson_voice == "male":
        return OpenAITTSVoices.ONYX
    elif lesson_voice == "female":
        return OpenAITTSVoices.NOVA
    else:
        return OpenAITTSVoices.ALLOY  # Default to Alloy for a gender-neutral default
