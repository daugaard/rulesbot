# Generated by Django 4.2.4 on 2023-08-24 01:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0004_document_public_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="card_image",
            field=models.ImageField(blank=True, default=None, null=True, upload_to=""),
        ),
        migrations.AlterField(
            model_name="document",
            name="public_url",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]