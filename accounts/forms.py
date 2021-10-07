

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User


class UserAdminCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = (
            "nickname",
            "email",
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=("Password"),
        help_text=(
            "Raw passwords are not stored, so there is no way to see "
            "this user's password, but you can change the password "
            'using <a href="../password/">this form</a>.'
        ),
    )

    class Meta:
        model = User
        fields = ("email", "nickname", "password", "is_active", "admin")

    def clean_password(self):
        return self.initial["password"]

# ...
class LoginForm(forms.Form):
    email = forms.EmailField(
        label="email",
        widget=forms.EmailInput(
            attrs={"class": "form-input", "placeholder": "enter email"}
        ),
    )
    password = forms.CharField(
        label="password",
        widget=forms.PasswordInput(
            attrs={"class": "form-input", "placeholder": "enter password"}
        ),
    )


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        label="smail",
        widget=forms.EmailInput(
            attrs={"class": "form-input", "placeholder": "enter email"}
        ),
    )
    nickname = forms.CharField(
        label="nickname",
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "enter nickname"}
        ),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-input", "placeholder": "enter password"}
        ),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-input", "placeholder": "confirm password"}
        ),
    )

    class Meta:
        model = User
        fields = ["email", "nickname"]
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-input", "placeholder": "enter email"}
            )
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.is_active = False
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = None

    class Meta:
        model = User
        fields = (
            "email",
            "nickname",
            "picture",
        )
