# Generated by Django 5.0.9 on 2024-09-07 17:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("lessons", "0013_alter_chatlesson_minigames"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="chatlesson",
            options={
                "verbose_name": "Chat Lesson",
                "verbose_name_plural": "Chat Lessons",
            },
        ),
        migrations.AlterModelTable(
            name="chatlesson",
            table="chat_lessons",
        ),
    ]
