# Generated by Django 4.2.4 on 2023-08-25 19:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0007_alter_game_card_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="slug",
            field=models.SlugField(blank=True, max_length=500, null=True),
        ),
    ]