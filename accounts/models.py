

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password=None,
        is_staff=False,
        is_admin=False,
        is_active=True,
    ):
        if not email:
            raise ValueError("User must have an Email")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.is_active = is_active
        user.admin = is_admin
        user.staff = is_staff
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password=None):
        user = self.create_user(
            email, password=password, is_staff=True
        )
        return user
    def create_superuser(self, email, password=None):
        user = self.create_user(
            email, password=password, is_staff=True, is_admin=True
        )
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    nickname = models.CharField(unique=True, max_length=30)
    picture = models.FileField(default="default.png", upload_to="profile_picture")
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    status_time = models.DateTimeField(auto_now_add=True, null=True)

    USERNAME_FIELD = "email"
    objects = UserManager()

    def __str__(self):
        return self.nickname

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        return self.staff
    @property
    def is_admin(self):
        return self.admin


class LoginAttempt(models.Model):
    user = models.OneToOneField(User, related_name='login_attempt_user', on_delete=models.CASCADE)
    login_attempts = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "user: {}, attempts: {}".format(self.user.email, self.login_attempts)
