

from django.urls import path
from .import views

urlpatterns = [
    path("all-users/", views.applicants_for_friends, name="friendship_view_users"),
    path(
        "all-friends/<nickname>/",
        views.view_friends,
        name="all_friends",
    ),
    path(
        "add-friend/<to_username>/",
        views.to_add_friend,
        name="add_friend",
    ),
    path(
        "friend-accept/<fr_rq>/",
        views.to_accept,
        name="to_accept",
    ),
    path(
        "friend-reject/<fr_rq>/",
        views.to_reject,
        name="to_reject",
    ),
    path(
        "friend-requests/",
        views.new_friend_requests,
        name="to_request_list",
    ),
    path(
        "friend-requests/rejected/",
        views.to_request_list_rejected,
        name="to_requests_rejected",
    ),
    path(
        "friend-request/<fr_rq>/",
        views.to_requests_detail,
        name="to_requests_detail",
    ),
    path(
        "friend-cancel/<fr_rq>/",
        views.to_cancel,
        name="to_cancel",
    ),
    # ...
    path(
        "delete/<to_id>/",
        views.delete_friend,
        name="friend_delete",
    ),

]
