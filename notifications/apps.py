

from django.apps import AppConfig


class Config(AppConfig):
    name = "notifications"

    def ready(self):
        super().ready()
        import notifications.signals
        notifications.notify = notifications.signals.notify
