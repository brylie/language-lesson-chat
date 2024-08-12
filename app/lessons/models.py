from django.db import models
from django.template.loader import render_to_string
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel


class KeyConcept(models.Model):
    lesson = ParentalKey(
        'Lesson', related_name='key_concepts', on_delete=models.CASCADE)
    concept = models.CharField(
        max_length=255,
        help_text="Enter a key language concept or vocabulary item for this lesson."
    )

    panels = [
        FieldPanel('concept'),
    ]

    def __str__(self):
        return self.concept


class Lesson(Page, ClusterableModel):
    intro = RichTextField(
        blank=True,
        help_text="Provide a brief introduction to the lesson. This will be shown to the student before they start the interactive dialogue."
    )
    cover_photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Choose an image that represents the setting or theme of the lesson. This will help set the scene for the student."
    )
    location = models.CharField(
        max_length=100,
        help_text="Specify the location or setting for this lesson (e.g., 'Coffee Shop', 'Airport', 'Art Gallery'). This will be used to set the context for the AI dialogue."
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
        default='a1',
        help_text="Select the CEFR level for this lesson. This will help tailor the AI's language complexity to the student's proficiency."
    )
    estimated_time = models.PositiveIntegerField(
        default=30,
        help_text="Estimate the time (in minutes) it will take to complete this lesson, including the interactive dialogue."
    )
    llm_system_prompt = models.TextField(
        verbose_name="LLM System Prompt",
        help_text="Provide specific instructions for the AI assistant's behavior in this lesson. For example, 'You are a friendly barista in a busy coffee shop. Engage the student in small talk and help them order a drink.'"
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('cover_photo'),
        FieldPanel('location'),
        FieldPanel('difficulty_level'),
        FieldPanel('estimated_time'),
        FieldPanel('llm_system_prompt'),
        InlinePanel('key_concepts', label="Key Concepts"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['key_concepts'] = self.key_concepts.all()

        # Generate the LLM prompt
        prompt_context = {
            'difficulty_level': self.get_difficulty_level_display(),
            'location': self.location,
            'system_prompt': self.llm_system_prompt,
            'key_concepts': [concept.concept for concept in self.key_concepts.all()],
        }
        context['llm_prompt'] = render_to_string(
            'lessons/prompt_template.txt', prompt_context)

        return context

    class Meta:
        verbose_name = "Language Lesson"
        verbose_name_plural = "Language Lessons"
