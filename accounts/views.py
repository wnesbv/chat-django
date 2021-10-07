

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import UpdateView
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from .forms import RegistrationForm, LoginForm
from .models import LoginAttempt, User
from .token import account_activation_token
from .decorators import unauthenticated_user
from .utils import send_user_email


@unauthenticated_user
def signup_page(request):
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            to_email = form.cleaned_data.get("email")
            current_site = get_current_site(request)
            mail_subject = "Activate your account"
            response = send_user_email(
                user,
                mail_subject,
                to_email,
                current_site,
                "accounts/email_verification.html",
            )
            if response == "success":
                messages.success(
                    request,
                    "We have sent you an activation link in your email."
                    "Please confirm your email to continue."
                    "Check your spam folder if you don't receive it",
                )
            else:
                messages.warning(
                    request,
                    "An warning. Please ensure you have good internet connection."
                    "Check your email address",
                )
                user.delete()

    context = {"form": form}
    return render(request, "accounts/signup.html", context)


@unauthenticated_user
def login_page(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            now = timezone.now()
            try:
                _user = User.objects.get(email=email)
                login_attempt, created = LoginAttempt.objects.get_or_create(user=_user)
                user = authenticate(request, username=email, password=password)
                if user is not None:
                    login(request, user)
                    login_attempt.login_attempts = 0
                    login_attempt.save()
                    return redirect(settings.LOGIN_REDIRECT_URL)

                else:
                    login_attempt.login_attempts += 1
                    login_attempt.timestamp = now
                    login_attempt.save()
                    if login_attempt.login_attempts == settings.MAX_LOGIN_ATTEMPTS:
                        _user.is_active = False
                        _user.save()
                        mail_subject = "Account suspended"
                        current_site = get_current_site(request)
                        send_user_email(
                            _user,
                            mail_subject,
                            email,
                            current_site,
                            "accounts/email_account_suspended.html",
                        )
                        messages.warning(
                            request,
                            "Account suspended, maximum login attempts exceeded"
                            "Reactivation link has been sent to your email",
                        )
                    else:
                        messages.warning(request, "Incorrect email or password")
                    return redirect(settings.LOGIN_URL)

            except ObjectDoesNotExist:
                messages.warning(request, "Object Does Not Exist")
                return redirect(settings.LOGIN_URL)

    context = {"form": form}
    return render(request, "accounts/login.html", context)


def activate_account_page(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login_attempt, created = LoginAttempt.objects.get_or_create(user=user)
        if login_attempt.login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            login_attempt.login_attempts = 0
            login_attempt.save()
            messages.success(request, "Account restored, you can now proceed to login")
        else:
            messages.success(
                request, "Thank you for confirming your email. You can now login."
            )
        return redirect(settings.LOGIN_URL)
    else:
        messages.warning(request, "Activation link is invalid!")
        return redirect(settings.LOGIN_URL)


def logout_view(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)


@login_required
def home(request):
    return render(request, "index.html")


class ProfileView(UpdateView):
    model = User
    fields = [
        "nickname",
        "picture",
    ]
    template_name = "accounts/profile.html"
    success_url = "/chat/"

    def get_object(self):
        return self.request.user
