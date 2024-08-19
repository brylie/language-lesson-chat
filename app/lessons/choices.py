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


class VoiceChoice(models.TextChoices):
    """
    Choices for different voices available for text-to-speech.
    """

    MALE = "male", _("Male")
    FEMALE = "female", _("Female")


class LanguageChoice(models.TextChoices):
    """
    Choices for different languages available for text-to-speech.
    """

    AFRIKAANS = "af", _("Afrikaans")
    ARABIC = "ar", _("Arabic")
    ARMENIAN = "hy", _("Armenian")
    AZERBAIJANI = "az", _("Azerbaijani")
    BELARUSIAN = "be", _("Belarusian")
    BOSNIAN = "bs", _("Bosnian")
    BULGARIAN = "bg", _("Bulgarian")
    CATALAN = "ca", _("Catalan")
    CHINESE = "zh", _("Chinese")
    CROATIAN = "hr", _("Croatian")
    CZECH = "cs", _("Czech")
    DANISH = "da", _("Danish")
    DUTCH = "nl", _("Dutch")
    ENGLISH = "en", _("English")
    ESTONIAN = "et", _("Estonian")
    FINNISH = "fi", _("Finnish")
    FRENCH = "fr", _("French")
    GALICIAN = "gl", _("Galician")
    GERMAN = "de", _("German")
    GREEK = "el", _("Greek")
    HEBREW = "he", _("Hebrew")
    HINDI = "hi", _("Hindi")
    HUNGARIAN = "hu", _("Hungarian")
    ICELANDIC = "is", _("Icelandic")
    INDONESIAN = "id", _("Indonesian")
    ITALIAN = "it", _("Italian")
    JAPANESE = "ja", _("Japanese")
    KANNADA = "kn", _("Kannada")
    KAZAKH = "kk", _("Kazakh")
    KOREAN = "ko", _("Korean")
    LATVIAN = "lv", _("Latvian")
    LITHUANIAN = "lt", _("Lithuanian")
    MACEDONIAN = "mk", _("Macedonian")
    MALAY = "ms", _("Malay")
    MARATHI = "mr", _("Marathi")
    MAORI = "mi", _("Maori")
    NEPALI = "ne", _("Nepali")
    NORWEGIAN = "no", _("Norwegian")
    PERSIAN = "fa", _("Persian")
    POLISH = "pl", _("Polish")
    PORTUGUESE = "pt", _("Portuguese")
    ROMANIAN = "ro", _("Romanian")
    RUSSIAN = "ru", _("Russian")
    SERBIAN = "sr", _("Serbian")
    SLOVAK = "sk", _("Slovak")
    SLOVENIAN = "sl", _("Slovenian")
    SPANISH = "es", _("Spanish")
    SWAHILI = "sw", _("Swahili")
    SWEDISH = "sv", _("Swedish")
    TAGALOG = "tl", _("Tagalog")
    TAMIL = "ta", _("Tamil")
    THAI = "th", _("Thai")
    TURKISH = "tr", _("Turkish")
    UKRAINIAN = "uk", _("Ukrainian")
    URDU = "ur", _("Urdu")
    VIETNAMESE = "vi", _("Vietnamese")
    WELSH = "cy", _("Welsh")
