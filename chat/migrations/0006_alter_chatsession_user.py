# Generated by Django 4.2.4 on 2023-10-30 01:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("chat", "0005_chatsession_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatsession",
            name="user",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="chat_sessions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]