# Generated by Django 4.2.16 on 2024-11-12 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vocab_mode", "0003_alter_vocabularybook_json_file"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vocabularybook",
            name="json_file",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="D:\\\\workspace\\\\eng_word\\\\utils\\\\json_words\\\\combined\\\\combined_word.json",
            ),
        ),
    ]
