

from django import template
from chat.models import MessageChat

register = template.Library()

# ...
@register.simple_tag
def chat_nickname(nick_chat):
    return MessageChat.objects.get(msg_chat=nick_chat.nickname)
