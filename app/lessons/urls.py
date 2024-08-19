from django.urls import path
from .views import generate_audio

urlpatterns = [
    path("generate-audio/<int:message_id>/", generate_audio, name="generate_audio"),
]
