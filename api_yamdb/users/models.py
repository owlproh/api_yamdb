from django.contrib.auth.models import AbstractUser
from django.db import models

ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'


class User(AbstractUser):
    roles = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
    )
    username = models.CharField(max_length=200, unique=True)
    email = models.EmailField('Email', max_length=150, unique=True)
    first_name = models.CharField('Имя', max_length=100, blank=True)
    last_name = models.CharField('Фамилия', max_length=100, blank=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(max_length=50, choices=roles, default=USER)
    confirmation_code = models.CharField('Код подтверждения',
                                         max_length=255,
                                         null=True)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_user(self):
        return self.role == 'user'
