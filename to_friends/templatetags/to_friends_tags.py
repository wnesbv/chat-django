

from django import template
from to_friends.models import Friend

register = template.Library()

@register.inclusion_tag("to_friends/tags_pattern/friend_requests.html")
def friend_requests(user):
    return {"friend_requests": Friend.objects.requests(user)}
