from django.contrib import admin

from games.services.document_ingestion_service import ingest_document

from .models import Document, Game


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 2


class GameAdmin(admin.ModelAdmin):
    inlines = [DocumentInline]
    list_display = (
        "name",
        "ingested",
        "created_at",
        "updated_at",
    )
    list_filter = ["ingested", "created_at", "updated_at"]
    search_fields = ["name"]
    actions = ["ingest_documents"]

    @admin.action(description="Ingest game documents")
    def ingest_documents(self, request, queryset):
        for game in queryset:
            # clear the vector store
            game.vector_store.clear()
            # ingest the documents
            for document in game.document_set.all():
                ingest_document(document)
            game.ingested = True
            game.save()
        self.message_user(request, "Documents ingested")


admin.site.register(Game, GameAdmin)
