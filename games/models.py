from django.db import models

from games.vectorstores import GameVectorStore


class Game(models.Model):
    name = models.CharField(max_length=500)
    ingested = models.BooleanField(default=False)

    card_image = models.ImageField(default=None, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    @property
    def vector_store(self):
        return GameVectorStore(self)


class Document(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=500)
    url = models.CharField(max_length=500)  # URL to ingest from
    public_url = models.CharField(
        max_length=1000, null=True, blank=True
    )  # URL to display to users
    ingested = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.display_name}"

    @property
    def display_url(self):
        return self.public_url or self.url
