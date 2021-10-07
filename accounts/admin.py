

from django.contrib.admin import ModelAdmin, site, register
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import User, LoginAttempt


class EmailUserAdmin(BaseUserAdmin):
    model = User
    search_fields = ["email"]
    list_display = [
        "email",
        "nickname",
        "is_active",
        "staff",
        "admin",
        "last_login",
        "timestamp",
    ]
    list_filter = ["is_active", "staff", "admin",]
    ordering = ["email"]
    filter_horizontal = []

    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    fieldsets = (
        (None, {"fields": ("email", "password",)}),
        ('Groups', {'fields': ('groups',)}),
        (
            "Personal info",
            {"fields": ("nickname", "picture",)},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "admin",
                    "staff",
                    "is_active",
                )
            },
        ),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )


@register(LoginAttempt)
class LoginAttemptAdmin(ModelAdmin):
    list_display = ["user", "login_attempts", "timestamp"]
    search_fields = ["user"]


site.register(User, EmailUserAdmin)
# admin.site.unregister(Group)
