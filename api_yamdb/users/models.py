from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    roles = (
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
        ('user', 'Пользователь'),
    )
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True
    )
    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=150
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(
        max_length=14,
        choices=roles
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=255,
        null=True
    )

    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_moderator(self):
        return self.role == 'moderator'
    
    @property
    def is_user(self):
        return self.role == 'user'
