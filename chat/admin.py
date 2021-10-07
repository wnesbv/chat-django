

from django.contrib.admin import ModelAdmin, site
from .models import MessageChat


class MessageChatAdmin(ModelAdmin):
    readonly_fields = ("created",)
    search_fields = (
        "id",
        "msg_chat",
        "user__nickname",
    )
    list_display = ("id", "nick_chat", "group_name", "created", "msg_chat")
    list_display_links = ("id",)
    list_filter = ("nick_chat", "group_name")
    date_hierarchy = "created"


site.register(MessageChat, MessageChatAdmin)
