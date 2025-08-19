import uuid

from django.contrib.auth.models import User
from django.db import models

from games.models import Document, Game


class ChatSession(models.Model):
    session_slug = models.SlugField(unique=True)
    game = models.ForeignKey(
        Game, on_delete=models.DO_NOTHING
    )  # Do not delete the session if the game is deleted

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name="chat_sessions",
    )  # If the user is deleted, keep the session but remove the user

    ip_address = models.GenericIPAddressField(null=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # on create generate a unique session slug
    def save(self, *args, **kwargs):
        if not self.session_slug:
            self.session_slug = str(uuid.uuid4())
        return super().save(*args, **kwargs)

    @classmethod
    def no_user_no_messages(cls):
        return (
            cls.objects.filter(user=None)
            .annotate(message_count=models.Count("message"))
            .filter(message_count=0)
        )


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


class SourceDocument(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    page_number = models.IntegerField()
