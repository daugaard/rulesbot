from django.contrib import admin

from chat.models import ChatSession, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ["message", "message_type", "created_at"]
    fields = ["message", "message_type", "created_at"]
    ordering = ["created_at"]
    show_change_link = True


class ChatSessionAdmin(admin.ModelAdmin):
    inlines = [MessageInline]
    list_display = (
        "id",
        "game_name",
        "number_of_messages",
        "user",
        "ip_address",
        "created_at",
        "updated_at",
    )
    list_filter = ["created_at", "updated_at", "user", "ip_address"]
    search_fields = ["ip_address"]

    def game_name(self, obj):
        return obj.game.name

    def number_of_messages(self, obj):
        return obj.message_set.count()


admin.site.register(ChatSession, ChatSessionAdmin)
