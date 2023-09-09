from django.db import models
from django.template.defaultfilters import slugify
from django_resized import ResizedImageField

from games.vectorstores import GameVectorStore


class Game(models.Model):
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, null=True, blank=True)
    ingested = models.BooleanField(default=False)

    card_image = ResizedImageField(
        default="games/card_images/default.png",
        null=False,
        upload_to="games/card_images",
        size=[900, None],
        quality=75,
    )
    faiss_file = models.FileField(
        upload_to="games/faiss_indexes", null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    @property
    def vector_store(self):
        return GameVectorStore(self)

    @property
    def rulebook_url(self):
        # Always return the display URL of the first document
        # Used to provide a rulebook link on the game page
        if self.document_set.count() == 0:
            return None
        return self.document_set.first().display_url

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Game, self).save(*args, **kwargs)


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
