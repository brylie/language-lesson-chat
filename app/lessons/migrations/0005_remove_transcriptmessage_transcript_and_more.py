# Generated by Django 5.0.8 on 2024-08-18 19:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0004_transcript_transcriptmessage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transcriptmessage',
            name='transcript',
        ),
        migrations.DeleteModel(
            name='Transcript',
        ),
        migrations.DeleteModel(
            name='TranscriptMessage',
        ),
    ]