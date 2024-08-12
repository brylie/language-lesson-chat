from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel


class KeyConcept(models.Model):
    lesson = ParentalKey(
        'Lesson', related_name='key_concepts', on_delete=models.CASCADE)
    concept = models.CharField(max_length=255)

    panels = [
        FieldPanel('concept'),
    ]

    def __str__(self):
        return self.concept


class Lesson(Page, ClusterableModel):
    intro = RichTextField(blank=True)
    cover_photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('a1', 'A1 - Beginner'),
            ('a2', 'A2 - Elementary'),
            ('b1', 'B1 - Intermediate'),
            ('b2', 'B2 - Upper Intermediate'),
            ('c1', 'C1 - Advanced'),
            ('c2', 'C2 - Proficiency'),
        ],
        default='a1'
    )
    estimated_time = models.PositiveIntegerField(
        help_text="Estimated time to complete the lesson (in minutes)",
        default=30
    )
    llm_system_prompt = models.TextField(
        verbose_name="LLM System Prompt",
        help_text="Provide the system prompt for the LLM agent to define its role and behavior.",
        blank=True
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('cover_photo'),
        FieldPanel('difficulty_level'),
        FieldPanel('estimated_time'),
        InlinePanel('key_concepts', label="Key Concepts"),
        FieldPanel('llm_system_prompt'),
    ]
