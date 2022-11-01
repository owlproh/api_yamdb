from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Genre(models.Model):
    "Модель жанров."
    pass


class Category(models.Model):
    "Модель категорий."
    pass


class Title(models.Model):
    "Модель произведений."
    pass


class Review(models.Model):
    "Модель отзывов."
    pass


class Comment(models.Model):
    "Модель комментариев."
    pass
