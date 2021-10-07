

from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.query import QuerySet
from django.utils.timesince import timesince as timesince_
from model_utils import Choices
from swapper import load_model
from notifications import settings as notifications_settings
from notifications.signals import notify
from notifications.utils import id2slug


EXTRA_DATA = notifications_settings.get_config()["USE_JSONFIELD"]
def is_soft_delete():
    return notifications_settings.get_config()["SOFT_DELETE"]

def assert_soft_delete():
    if not is_soft_delete():
        msg = "REVERTME"
        raise ImproperlyConfigured(msg)


class NotificationQuerySet(models.query.QuerySet):
    def unsent(self):
        return self.filter(emailed=False)

    def sent(self):
        return self.filter(emailed=True)

    def unread(self, include_deleted=False):
        """Возвращайте только непрочитанные элементы в текущем наборе запросов"""
        if is_soft_delete() and not include_deleted:
            return self.filter(unread=True, deleted=False)
        return self.filter(unread=True)

    def read(self, include_deleted=False):
        """Возвращайте только прочитанные элементы в текущем наборе запросов"""
        if is_soft_delete() and not include_deleted:
            return self.filter(unread=False, deleted=False)
        return self.filter(unread=False)

    def mark_all_as_read(self, recipient=None):
        # Мы хотим отфильтровать прочитанные, так как позже мы сохраним
        # время, когда они были помечены как прочитанные.
        qset = self.unread(True)
        if recipient:
            qset = qset.filter(recipient=recipient)
        return qset.update(unread=False)

    def mark_all_as_unread(self, recipient=None):
        qset = self.read(True)
        if recipient:
            qset = qset.filter(recipient=recipient)
        return qset.update(unread=True)

    def deleted(self):
        """Возвращайте только удаленные элементы в текущем наборе запросов"""
        assert_soft_delete()
        return self.filter(deleted=True)

    def active(self):
        """Возвращает только активные(не удаленные) элементы в текущем наборе запросов"""
        assert_soft_delete()
        return self.filter(deleted=False)

    def mark_all_as_deleted(self, recipient=None):
        assert_soft_delete()
        qset = self.active()
        if recipient:
            qset = qset.filter(recipient=recipient)
        return qset.update(deleted=True)

    def mark_all_as_active(self, recipient=None):
        assert_soft_delete()
        qset = self.deleted()
        if recipient:
            qset = qset.filter(recipient=recipient)
        return qset.update(deleted=False)

    def mark_as_unsent(self, recipient=None):
        qset = self.sent()
        if recipient:
            qset = qset.filter(recipient=recipient)
        return qset.update(emailed=False)

    def mark_as_sent(self, recipient=None):
        qset = self.unsent()
        if recipient:
            qset = qset.filter(recipient=recipient)
        return qset.update(emailed=True)


class AbstractNotification(models.Model):
    LEVELS = Choices("success", "info", "warning", "error")
    level = models.CharField(choices=LEVELS, default=LEVELS.info, max_length=20)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        null=True,
        related_name="notifications",
        on_delete=models.CASCADE,
    )
    unread = models.BooleanField(default=True, blank=False, db_index=True)
    actor_content_type = models.ForeignKey(
        ContentType, related_name="notify_actor", on_delete=models.CASCADE
    )
    actor_object_id = models.CharField(max_length=255)
    actor = GenericForeignKey("actor_content_type", "actor_object_id")
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    target_content_type = models.ForeignKey(
        ContentType,
        related_name="notify_target",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = GenericForeignKey("target_content_type", "target_object_id")
    action_object_content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name="notify_action_object",
        on_delete=models.CASCADE,
    )
    action_object_object_id = models.CharField(max_length=255, blank=True, null=True)
    action_object = GenericForeignKey(
        "action_object_content_type", "action_object_object_id"
    )

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    public = models.BooleanField(default=True, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)
    emailed = models.BooleanField(default=False, db_index=True)
    data = models.JSONField(blank=True, null=True)
    objects = NotificationQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ("-timestamp",)
        index_together = ("recipient", "unread")

    def __str__(self):
        ctx = {
            "actor": self.actor,
            "verb": self.verb,
            "action_object": self.action_object,
            "target": self.target,
            "timesince": self.timesince(),
        }
        if self.target:
            if self.action_object:
                return (
                    u"%(actor)s %(verb)s %(action_object)s on %(target)s %(timesince)s ago"
                    % ctx
                )
            return u"%(actor)s %(verb)s %(target)s %(timesince)s ago" % ctx
        if self.action_object:
            return u"%(actor)s %(verb)s %(action_object)s %(timesince)s ago" % ctx
        return u"%(actor)s %(verb)s %(timesince)s ago" % ctx

    def timesince(self, now=None):
        return timesince_(self.timestamp, now)

    @property
    def slug(self):
        return id2slug(self.id)

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()

    def mark_as_unread(self):
        if not self.unread:
            self.unread = True
            self.save()


def notify_handler(verb, **kwargs):
    kwargs.pop("signal", None)
    recipient = kwargs.pop("recipient")
    actor = kwargs.pop("sender")
    optional_objs = [
        (kwargs.pop(opt, None), opt) for opt in ("target", "action_object")
    ]
    public = bool(kwargs.pop("public", True))
    description = kwargs.pop("description", None)
    timestamp = kwargs.pop("timestamp", timezone.now())
    Notification = load_model("notifications", "Notification")
    level = kwargs.pop("level", Notification.LEVELS.info)

    if isinstance(recipient, Group):
        recipients = recipient.user_set.all()
    elif isinstance(recipient, (QuerySet, list)):
        recipients = recipient
    else:
        recipients = [recipient]
    new_notifications = []

    for recipient in recipients:
        newnotify = Notification(
            recipient=recipient,
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            verb=str(verb),
            public=public,
            description=description,
            timestamp=timestamp,
            level=level,
        )

        for obj, opt in optional_objs:
            if obj is not None:
                setattr(newnotify, "%s_object_id" % opt, obj.pk)
                setattr(
                    newnotify,
                    "%s_content_type" % opt,
                    ContentType.objects.get_for_model(obj),
                )

        if kwargs and EXTRA_DATA:
            newnotify.data = kwargs

        newnotify.save()
        new_notifications.append(newnotify)
    return new_notifications

notify.connect(notify_handler, dispatch_uid="notifications.models.notification")
