

from swapper import swappable_setting
from .base.models import AbstractNotification


class Notification(AbstractNotification):

    class Meta(AbstractNotification.Meta):
        abstract = False
        swappable = swappable_setting('notifications', 'Notification')
