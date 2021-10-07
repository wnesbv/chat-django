

from django.urls import path
from .import views


urlpatterns = [
    path("", views.index, name="chat"),
    path("<slug:room_name>/", views.room, name="room"),
    # ...
    path("chat-user", views.index_user, name="chat_user"),
    path("chat-friends", views.friends_user, name="chat_friends"),
    # ...
    path("update/<int:pk>/", views.MessageChatUpdate.as_view(), name="update"),
    path("delete/<int:pk>/", views.MessageChatDelete.as_view(), name="delete"),
]
