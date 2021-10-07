

import json
from django.utils import timezone
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from notifications.signals import notify
from accounts.models import User
from .models import MessageChat



class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_group_name = self.scope["url_route"]["kwargs"]["room_name"]
        await self.get_name(True)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send_status()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.get_name(False)
        await self.get_time(timezone.now())
        await self.send_status()

    @sync_to_async
    def send_status(self):
        self.send()


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = str(self.scope["user"])
        now_time = timezone.localtime().strftime(settings.TIME_FORMAT)
        await self.save_message(message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "user": user,
                "message": message,
                "now_time": now_time,
            },
        )

    async def chat_message(self, event):
        user = event["user"]
        message = event["message"]
        now_time = event["now_time"]
        await self.send(
            text_data=json.dumps(
                {
                    "user": user,
                    "message": message,
                    "now_time": now_time,
                }
            )
        )


    @sync_to_async
    def save_message(self, msg_chat):
        MessageChat.objects.create(
            nick_chat=self.scope["user"],
            msg_chat=msg_chat,
            group_name=self.room_group_name,
        )
        to_group = MessageChat.objects.filter(
            group_name=self.room_group_name
        )
        to_target = MessageChat.objects.latest(
            "group_name"
        )
        to_action_object = User.objects.filter(
            nick_name_chat__in=to_group
        ).last()

        to_notify = User.objects.exclude(nickname=self.scope["user"]).filter(
            nick_name_chat__in=to_group
        ).last()
        notify.send(
            self.scope["user"],
            recipient=to_notify,
            verb="new..",
            target=to_target,
            action_object=to_action_object,
        )


    @sync_to_async
    def get_name(self, status):
        return User.objects.filter(pk=self.scope["user"].pk).update(status=status)

    @sync_to_async
    def get_time(self, status_time):
        return User.objects.filter(pk=self.scope["user"].pk).update(status_time=status_time)
