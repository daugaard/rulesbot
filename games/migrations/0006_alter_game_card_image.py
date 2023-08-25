# Generated by Django 4.2.4 on 2023-08-25 14:03

import django_resized.forms
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0005_game_card_image_alter_document_public_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="card_image",
            field=django_resized.forms.ResizedImageField(
                blank=True,
                crop=None,
                default=None,
                force_format=None,
                keep_meta=True,
                null=True,
                quality=75,
                scale=None,
                size=[900, None],
                upload_to="games/card_images",
            ),
        ),
    ]