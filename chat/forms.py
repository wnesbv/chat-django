

from django.forms import ModelForm, Textarea
from .models import MessageChat


class MessageChatForm(ModelForm):
    class Meta:
        model = MessageChat
        fields = ("msg_chat",)
        widgets = {
            "msg_chat": Textarea(attrs={"rows": 4}),
        }
