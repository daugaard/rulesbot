import uuid
from django.db import models

from games.models import Game


class ChatSession(models.Model):
    session_slug = models.SlugField(unique=True)
    game = models.ForeignKey(
        Game, on_delete=models.DO_NOTHING
    )  # Do not delete the session if the game is deleted

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # on create generate a unique session slug
    def save(self, *args, **kwargs):
        if not self.session_slug:
            self.session_slug = str(uuid.uuid4())
        return super().save(*args, **kwargs)


class Message(models.Model):
    MESSAGE_TYPES = (("system", "System"), ("human", "Human"), ("ai", "AI"))
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    message = models.TextField()
    message_type = models.CharField(
        max_length=10, choices=MESSAGE_TYPES, default="human"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("updated_at",)
