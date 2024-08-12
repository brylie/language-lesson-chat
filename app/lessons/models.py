from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField


class Lesson(Page):
    intro = RichTextField(blank=True)
    cover_photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
