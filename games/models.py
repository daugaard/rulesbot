from django.db import models

from games.vectorstores import GameVectorStore

    

class Game(models.Model):
    name = models.CharField(max_length=500)
    ingested = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    vector_store_binary = models.BinaryField(null=True)

    def __str__(self):
        return f"{self.name}"
    
    @property
    def vector_store(self):
        return GameVectorStore(self)
    
    @property
    def vector_store_binary_size(self):
        return len(self.vector_store_binary) if self.vector_store_binary else 0


class Document(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=500)
    url = models.CharField(max_length=500)
    ingested = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.display_name}"