import textwrap as tw

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    roles = (
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
        ('user', 'Пользователь'),
    )
    username = models.CharField('Логин', max_length=200, unique=True)
    email = models.EmailField('Email', max_length=150, unique=True)
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(max_length=50, choices=roles)
    confirmation_code = models.CharField('Код подтверждения', max_length=255, null=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return tw.shorten(self.username, width=15, placeholder='...')