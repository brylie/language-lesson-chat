from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Lesson, Transcript, TranscriptMessage

User = get_user_model()

class TranscriptModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.lesson = Lesson.objects.create(title='Test Lesson')

    def test_transcript_creation(self):
        transcript = Transcript.objects.create(user=self.user, lesson=self.lesson)
        self.assertEqual(transcript.user, self.user)
        self.assertEqual(transcript.lesson, self.lesson)
        self.assertIsNotNone(transcript.created_at)

    def test_transcript_message_creation(self):
        transcript = Transcript.objects.create(user=self.user, lesson=self.lesson)
        message = TranscriptMessage.objects.create(
            transcript=transcript,
            role='user',
            content='Test message',
            key_concept='Test concept'
        )
        self.assertEqual(message.transcript, transcript)
        self.assertEqual(message.role, 'user')
        self.assertEqual(message.content, 'Test message')
        self.assertEqual(message.key_concept, 'Test concept')
        self.assertIsNotNone(message.created_at)


class LessonModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.lesson = Lesson.objects.create(title='Test Lesson')

    def test_create_transcript(self):
        request = self.client.request().wsgi_request
        request.user = self.user
        transcript = self.lesson.create_transcript(request)
        self.assertEqual(transcript.user, self.user)
        self.assertEqual(transcript.lesson, self.lesson)
        self.assertEqual(request.session['transcript_id'], transcript.id)

    def test_log_message(self):
        request = self.client.request().wsgi_request
        request.user = self.user
        transcript = self.lesson.create_transcript(request)
        request.session['transcript_id'] = transcript.id

        self.lesson.log_message(request, 'user', 'Test user message', 'Test concept')
        self.lesson.log_message(request, 'assistant', 'Test assistant message', 'Test concept', 'gpt-4-0613')

        messages = TranscriptMessage.objects.filter(transcript=transcript)
        self.assertEqual(messages.count(), 2)

        user_message = messages.get(role='user')
        self.assertEqual(user_message.content, 'Test user message')
        self.assertEqual(user_message.key_concept, 'Test concept')

        assistant_message = messages.get(role='assistant')
        self.assertEqual(assistant_message.content, 'Test assistant message')
        self.assertEqual(assistant_message.key_concept, 'Test concept')
        self.assertEqual(assistant_message.llm_model, 'gpt-4-0613')
