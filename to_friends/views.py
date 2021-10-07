


from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from notifications.signals import notify
from accounts.models import User
from .models import FriendshipRequest, Friend
from .forms import FriendshipRequestForm


def get_friendship_context_object_name():
    return getattr(settings, "", "user")
def get_friendship_context_object_list_name():
    return getattr(settings, "", "users")


# претенденты на дружбу
def applicants_for_friends(request, template_name="to_friends/user_actions.html"):
    to_request = request.user.nickname
    from_request = FriendshipRequest.objects.prefetch_related("from_user").filter(
        from_user=request.user
    )
    from_friend = Friend.objects.prefetch_related("from_user").filter(
        from_user=request.user
    )
    users = (
        User.objects.exclude(nickname__in=to_request)
        .exclude(friendship_requests_received__in=from_request)
        .exclude(to_user_friends__in=from_friend)
        .exclude(nickname=request.user.nickname)
    )
    return render(
        request, template_name, {get_friendship_context_object_list_name(): users}
    )

# Создайте запрос на дружбу
@login_required
def to_add_friend(request, to_username, template_name="to_friends/add.html"):
    form = FriendshipRequestForm(request.POST)
    ctx = {"form": form, "to_username": to_username}

    if request.method == "POST":
        accompanying_text = form
        from_friends = request.user
        to_friends = User.objects.get(nickname=to_username)

        if form.is_valid():
            form.instance.from_user = request.user
            form.instance.to_user = to_friends
            form.save()
            ctx = {
                "from_friends": from_friends,
                "to_friends": to_friends,
                "accompanying_text": accompanying_text,
            }

            f_request = FriendshipRequest.objects.latest("id")

            notify.send(
                request.user,
                recipient=to_friends,
                verb="friendship request",
                target=f_request,
                action_object=from_friends,
            )
            messages.success(
                request,
                "Ok, the request has been sent and is waiting for confirmation",
            )
            return redirect("to_request_list")
    return render(request, template_name, ctx)

#  Просмотр друзей пользователя
def view_friends(request, nickname):
    to_request = User.objects.filter(nickname=nickname)
    from_friend = Friend.objects.prefetch_related("from_user").filter(
        from_user=request.user
    )
    friends_nickname = (
        User.objects.exclude(nickname__in=to_request)
        .filter(to_user_friends__in=from_friend)
        .exclude(nickname=request.user.nickname)
    )
    return render(
        request,
        "to_friends/user_list.html",
        {
            "friends_nickname": friends_nickname,
        },
    )

#  Принятие дружбы
@login_required
def to_accept(request, fr_rq):
    if request.method == "POST":
        f_request = get_object_or_404(
            request.user.friendship_requests_received, id=fr_rq
        )
        f_request.accept()
        to_name = Friend.objects.latest("to_user")
        from_name = Friend.objects.latest("from_user")
        to_object = Friend.objects.all()
        to_notify = User.objects.filter(
            from_user_friends__in=to_object
        ).first()
        to_friend = Friend.objects.latest("id")

        # notify ...
        notify.send(
            from_name,
            recipient=to_notify,
            verb="accepted friendship",
            target=to_friend,
            action_object=to_name,
        )
        messages.success(
            request,
            "Ok, now you are friends",
        )
        return redirect("all_friends", nickname=request.user.nickname)
    return redirect("to_requests_detail", fr_rq=fr_rq)

# Отклонить просьбу о дружбе
@login_required
def to_reject(request, fr_rq):
    if request.method == "POST":
        f_request = get_object_or_404(
            request.user.friendship_requests_received, id=fr_rq
        )
        f_request.reject()
        return redirect("to_request_list")
    return redirect("to_requests_detail", fr_rq=fr_rq)

# Отмените ранее созданный идентификатор fr_rq
@login_required
def to_cancel(request, fr_rq):
    if request.method == "POST":
        f_request = get_object_or_404(
            request.user.friendship_requests_sent, id=fr_rq
        )
        f_request.cancel()
        return redirect("to_request_list")
    return redirect("to_requests_detail", fr_rq=fr_rq)

# Просмотр конкретного запроса на дружбу
@login_required
def to_requests_detail(
    request, fr_rq, template_name="to_friends/request.html"
):
    f_request = get_object_or_404(FriendshipRequest, id=fr_rq)
    return render(request, template_name, {"friendship_request": f_request})


# ...
@login_required
def new_friend_requests(request, template_name="to_friends/new_requests.html"):
    friendship_requests = Friend.objects.requests(request.user)
    friendship_requests = FriendshipRequest.objects.filter(rejected__isnull=True)
    return render(request, template_name, {"requests": friendship_requests})

@login_required
def to_request_list_rejected(request, template_name="to_friends/rejected_list.html"):
    # friendship_requests = Friend.objects.rejected_requests(request.user)
    friendship_requests = FriendshipRequest.objects.filter(rejected__isnull=False)
    return render(request, template_name, {"requests": friendship_requests})


@login_required
def delete_friend(request, to_id, template_name="to_friends/delete.html"):
    friend_tofrom_delete = Friend.objects.get(to_user=to_id, from_user=request.user)
    if request.method == "POST":
        friend_tofrom_delete.friend_delete()
        messages.success(
            request,
            "Ok, delete",
        )
        return redirect("friendship_view_users")
    return render(request, template_name)
