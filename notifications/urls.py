

from django.urls import path
from .import views

app_name = "notifications"

urlpatterns = [
    path("", views.AllNotificationsList.as_view(), name="all"),
    path("unread/", views.UnreadNotificationsList.as_view(), name="unread"),

    path("mark-all-as-read/", views.mark_all_as_read, name="mark_all_as_read"),
    # отметить как прочитанное
    path("mark-as-read/<slug>/", views.mark_as_read, name="mark_as_read"),
    path(
        "mark-as-unread/<slug>/", views.mark_as_unread, name="mark_as_unread"
    ),
    path("delete/<slug>/", views.delete, name="delete"),
    path(
        "api/unread_count/",
        views.live_unread_notification_count,
        name="live_unread_notification_count",
    ),
    path(
        "api/all_count/",
        views.live_all_notification_count,
        name="live_all_notification_count",
    ),
    path(
        "api/unread_list/",
        views.live_unread_notification_list,
        name="live_unread_notification_list",
    ),
    path(
        "api/all_list/",
        views.live_all_notification_list,
        name="live_all_notification_list",
    ),
]
