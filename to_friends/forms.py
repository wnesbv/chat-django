

from django.forms import ModelForm, Textarea
from .models import FriendshipRequest


class FriendshipRequestForm(ModelForm):

    class Meta:
        model = FriendshipRequest
        fields = ("accompanying_text",)
        widgets = {
            "accompanying_text": Textarea(attrs={"cols": 80, "rows": 5}),
        }
