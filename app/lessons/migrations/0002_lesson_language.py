# Generated by Django 5.0.8 on 2024-08-15 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lessons", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="lesson",
            name="language",
            field=models.CharField(
                default="English",
                help_text="Specify the target language for this lesson (e.g., 'English', 'Spanish', 'French'). This will help the AI assistant provide appropriate responses and suggestions.",
                max_length=100,
            ),
            preserve_default=False,
        ),
    ]
