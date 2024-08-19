from django.db import models
from django.utils.translation import gettext_lazy as _


class CEFRLevel(models.TextChoices):
    """
    The Common European Framework of Reference for Languages (CEFR) is an international standard for describing language ability.

    The CEFR levels are a way of describing a person's language proficiency in a foreign language. They are used by language schools and language testing organizations to evaluate a person's language proficiency.
    """

    A1 = "a1", _("A1 - Beginner")
    A2 = "a2", _("A2 - Elementary")
    B1 = "b1", _("B1 - Intermediate")
    B2 = "b2", _("B2 - Upper Intermediate")
    C1 = "c1", _("C1 - Advanced")
    C2 = "c2", _("C2 - Proficiency")
