from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator

from users.constants import (
    MAX_NAME_LENGTH,
    MAX_ROLE_LENGTH,
)
from users.validators import required_username


class CustomUser(AbstractUser):
    USER_ROLE = 'user'
    ADMIN_ROLE = 'admin'
    ROLE_CHOICES = [
        (USER_ROLE, 'User'),
        (ADMIN_ROLE, 'Administrator'),
    ]

    username = models.CharField(
        verbose_name='Логин',
        max_length=MAX_NAME_LENGTH,
        unique=True,
        validators=[
            UnicodeUsernameValidator(
                message='Недопустимые символы в нике.'
            ),
            required_username
        ]
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Почта')
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_NAME_LENGTH,
        default='Не указано'
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_NAME_LENGTH,
        default='Не указано'
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=MAX_ROLE_LENGTH,
        choices=ROLE_CHOICES,
        default=USER_ROLE
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def has_user_role(self):
        return self.role == self.USER_ROLE

    def has_admin_role(self):
        return (self.role == self.ADMIN_ROLE
                or self.is_superuser)
