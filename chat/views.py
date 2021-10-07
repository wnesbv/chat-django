

from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from to_friends.models import Friend
from accounts.models import User
from .models import MessageChat
from .forms import MessageChatForm


def index(request):
    return render(request, "chat/index.html")


def room(request, room_name):
    chat_messages = MessageChat.objects.filter(group_name=room_name).order_by("created")

    paginator = Paginator(chat_messages, 4)
    page_request_variable = "page"
    page_number = request.GET.get(page_request_variable)

    try:
        paginated_queryset = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    return render(
        request,
        "chat/room.html",
        {
            "chat_messages": paginated_queryset,
            "room_name": room_name,
            "page_request_variable": page_request_variable,
        },
    )


# ... user


@login_required
def index_user(request):
    user_index = User.objects.all()

    return render(
        request,
        "chat/user_index.html",
        {
            "user_index": user_index,
        },
    )


# ... friends


@login_required
def friends_user(request):
    to_request = request.user.nickname
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
        "chat/user_friends.html",
        {
            "friends_nickname": friends_nickname,
        },
    )


class MessageChatUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = MessageChat
    form_class = MessageChatForm
    template_name = "chat/update.html"

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chat_messages"] = get_object_or_404(
            MessageChat, pk=self.kwargs.get("pk")
        )
        return context

    def post(self, request, *args, **kwargs):
        form = MessageChatForm(request.POST, request.FILES)
        messages.success(
            request,
            "the message has been edited",
        )
        return super().post(
            {
                "form": form,
            },
            request,
            *args,
            **kwargs
        )

    def form_valid(self, form):
        form.instance.nick_chat = self.request.user
        return super().form_valid(form)

    def test_func(self):
        ms = self.get_object()
        if self.request.user == ms.nick_chat:
            return True
        return False


class MessageChatDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = MessageChat
    template_name = "chat/delete.html"
    success_url = reverse_lazy("chat")

    def post(self, request, *args, **kwargs):
        messages.success(
            request,
            "the message was deleted",
        )
        return self.delete(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.nick_chat = self.request.user
        return super().form_valid(form)

    def test_func(self):
        ms = self.get_object()
        if self.request.user == ms.nick_chat:
            return True
        return False
