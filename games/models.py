import enum
from django.db import models

    

class Game(models.Model):
    name = models.CharField(max_length=500)
    ingested = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class Document(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=500)
    url = models.CharField(max_length=500)
    ingested = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.display_name}"