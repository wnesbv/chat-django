

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from .signals import (
    friendship_request_accepted,
    friendship_request_canceled,
    friendship_request_rejected,
    friendship_request_viewed,
)


class FriendshipRequest(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friendship_requests_sent",
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friendship_requests_received",
    )

    accompanying_text = models.TextField(_("accompanying text"), blank=True)
    created = models.DateTimeField(auto_now_add=True)
    rejected = models.DateTimeField(blank=True, null=True)
    viewed = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _("Friendship Request")
        verbose_name_plural = _("Friendship Requests")

    def __str__(self):
        return "/to-friends/friend-request/{}".format(self.id)

# ...
    def accept(self):
        Friend.objects.create(from_user=self.from_user, to_user=self.to_user)
        Friend.objects.create(from_user=self.to_user, to_user=self.from_user)
        friendship_request_accepted.send(
            sender=self, from_user=self.from_user, to_user=self.to_user
        )
        self.delete()
        FriendshipRequest.objects.filter(
            from_user=self.to_user, to_user=self.from_user
        ).delete()
        return True

    def reject(self):
        self.rejected = timezone.now()
        self.save()
        friendship_request_rejected.send(sender=self)
        return True

    def cancel(self):
        self.delete()
        friendship_request_canceled.send(sender=self)
        return True

    def mark_viewed(self):
        self.viewed = timezone.now()
        friendship_request_viewed.send(sender=self)
        self.save()
        return True

class FriendsManager(models.Manager):
    def requests(self, user):
        requests = self.requests
        if requests is None:
            qs = FriendshipRequest.objects.prefetch_related("to_user").filter(
                to_user=user
            )
            requests = list(qs)
        return requests

    def rejected_requests(self, user):
        rejected_requests = self.rejected_requests
        if rejected_requests is None:
            qs = (
                FriendshipRequest.objects.select_related("from_user", "to_user")
                .filter(to_user=user, rejected__isnull=False)
                .all()
            )
            rejected_requests = list(qs)
        return rejected_requests

class Friend(models.Model):
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="to_user_friends"
    )
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="from_user_friends"
    )
    created = models.DateTimeField(auto_now_add=True)

    objects = FriendsManager()

    class Meta:
        verbose_name = _("Friend")
        verbose_name_plural = _("Friends")

    def __str__(self):
        return "/to-friends/all-friends/{}".format(self.to_user)

    def friend_delete(self):
        Friend.objects.get(from_user=self.from_user, to_user=self.to_user).delete()
        Friend.objects.get(from_user=self.to_user, to_user=self.from_user).delete()
        return True
