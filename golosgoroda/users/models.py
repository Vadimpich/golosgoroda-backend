from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("У пользователя должен быть email")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(unique=True, max_length=150)
    email = models.EmailField(unique=True, verbose_name="Email")
    password = models.CharField(max_length=150, verbose_name="Пароль")
    is_staff = models.BooleanField(default=False, verbose_name="Менеджер")
    is_superuser = models.BooleanField(default=False, verbose_name="Администратор")

    USERNAME_FIELD = 'username'

    objects = CustomUserManager()
