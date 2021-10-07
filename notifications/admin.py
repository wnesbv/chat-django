

from django.contrib.admin import ModelAdmin, site
from swapper import load_model

Notification = load_model("notifications", "Notification")

class NotificationAdmin(ModelAdmin):
    raw_id_fields = ("recipient",)

    list_display = ("actor", "recipient", "timestamp", "level", "target", "unread", "public")
    list_filter = (
        "level",
        "unread",
        "public",
        "timestamp",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("actor")


site.register(Notification, NotificationAdmin)
