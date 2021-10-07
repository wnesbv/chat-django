

from django.db import models
from django.urls import reverse
from accounts.models import User


class MessageChat(models.Model):
    nick_chat = models.ForeignKey(User, related_name="nick_name_chat", on_delete=models.CASCADE)
    group_name = models.SlugField(max_length=30)
    msg_chat = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "/chat/{}".format(self.group_name)

    def get_absolute_url(self):
        return reverse(
            "room",
            kwargs={'room_name': str(self.group_name)}
        )
