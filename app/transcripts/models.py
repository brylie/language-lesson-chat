from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Transcript(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transcripts",
    )
    lesson = models.ForeignKey(
        "lessons.ChatLesson",
        on_delete=models.CASCADE,
        related_name="transcripts",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transcript for {self.user.username} - {self.lesson.title}"

    class Meta:
        ordering = ["-created_at"]
        db_table = "transcripts"


class TranscriptMessage(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    transcript = models.ForeignKey(
        Transcript,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
    )
    content = models.TextField()
    key_concept = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    llm_model = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["created_at"]
        db_table = "transcript_messages"

    def __str__(self):
        return f"{self.role} message in {self.transcript}"
