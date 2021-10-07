

from django.urls import path
from django.contrib.auth import views as auth_views
from .import views

app_name = "accounts"

urlpatterns = [
    path(
        "accounts/reset-password",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html"
        ),
        name="reset_password",
    ),
    path(
        "accounts/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_sent.html"
        ),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_form.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_complete",
    ),
    # Change Password
    path(
        "change-password/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/change_password.html", success_url="/"
        ),
        name="change_password",
    ),
    # ...
    path("accounts/signup/", views.signup_page, name="signup"),
    path(
        "accounts/activate/<slug:uidb64>/<slug:token>/",
        views.activate_account_page,
        name="activate",
    ),
    path("accounts/login/", views.login_page, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("", views.home, name="home"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]
