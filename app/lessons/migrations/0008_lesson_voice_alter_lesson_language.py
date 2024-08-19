# Generated by Django 5.0.8 on 2024-08-19 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0007_alter_lesson_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='voice',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female')], default='male', help_text="Select the voice for the text-to-speech playback. This will help tailor the audio experience to the student's preference.", max_length=20),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='language',
            field=models.CharField(choices=[('af', 'Afrikaans'), ('ar', 'Arabic'), ('hy', 'Armenian'), ('az', 'Azerbaijani'), ('be', 'Belarusian'), ('bs', 'Bosnian'), ('bg', 'Bulgarian'), ('ca', 'Catalan'), ('zh', 'Chinese'), ('hr', 'Croatian'), ('cs', 'Czech'), ('da', 'Danish'), ('nl', 'Dutch'), ('en', 'English'), ('et', 'Estonian'), ('fi', 'Finnish'), ('fr', 'French'), ('gl', 'Galician'), ('de', 'German'), ('el', 'Greek'), ('he', 'Hebrew'), ('hi', 'Hindi'), ('hu', 'Hungarian'), ('is', 'Icelandic'), ('id', 'Indonesian'), ('it', 'Italian'), ('ja', 'Japanese'), ('kn', 'Kannada'), ('kk', 'Kazakh'), ('ko', 'Korean'), ('lv', 'Latvian'), ('lt', 'Lithuanian'), ('mk', 'Macedonian'), ('ms', 'Malay'), ('mr', 'Marathi'), ('mi', 'Maori'), ('ne', 'Nepali'), ('no', 'Norwegian'), ('fa', 'Persian'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('ro', 'Romanian'), ('ru', 'Russian'), ('sr', 'Serbian'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('es', 'Spanish'), ('sw', 'Swahili'), ('sv', 'Swedish'), ('tl', 'Tagalog'), ('ta', 'Tamil'), ('th', 'Thai'), ('tr', 'Turkish'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('vi', 'Vietnamese'), ('cy', 'Welsh')], help_text="Specify the target language for this lesson (e.g., 'English', 'Spanish', 'French'). This will help the AI assistant provide appropriate responses and suggestions.", max_length=100),
        ),
    ]