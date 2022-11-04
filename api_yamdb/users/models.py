import textwrap as tw

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .enums import UserRoles

class User(AbstractUser):
    """Модель пользователей."""
    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
        db_index=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Имя пользователя содержит недопустимый символ'
        )]
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='email',
        unique=True
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        blank=True
    )
    bio = models.TextField(
        verbose_name='Биография пользователя',
        blank=True
    )
    role = models.CharField(
        max_length=UserRoles.max_length_choices(),
        verbose_name='Роль',
        choices=UserRoles.choices(),
        default=UserRoles.user.name
    )
    # confirmation_code = ?

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return tw.shorten(self.username, width=15, placeholder='...')