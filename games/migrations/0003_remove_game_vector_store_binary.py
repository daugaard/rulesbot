# Generated by Django 4.2.4 on 2023-08-15 02:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0002_game_vector_store_binary"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="game",
            name="vector_store_binary",
        ),
    ]
