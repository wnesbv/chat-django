

from django.template import Library
from django.utils.html import format_html
from ..models import User

register = Library()

@register.simple_tag
def on_user():
    user_status = User.objects.filter(status=True).all()
    html = "<i class='bi bi-record-circle'></i>".format(user_status=user_status)
    return format_html(html)
