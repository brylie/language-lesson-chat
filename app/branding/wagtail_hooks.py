from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel
from wagtail.images.models import Image
from django.db import models


# registers a setting that allows you to add a logo image to the website
@register_setting
class BrandingSettings(BaseSiteSetting):
    logo = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        # verbose name can be changed later when needed
        verbose_name="Company Logo"
    )

    panels = [
        FieldPanel('logo'),
    ]