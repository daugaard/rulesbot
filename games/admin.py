from django.contrib import admin

from .models import Game, Document

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 2

class GameAdmin(admin.ModelAdmin):
    inlines = [DocumentInline]
    list_display = ("name", "ingested", "created_at", "updated_at")
    list_filter = ["ingested", "created_at", "updated_at"]
    search_fields = ["name"]


admin.site.register(Game, GameAdmin)
