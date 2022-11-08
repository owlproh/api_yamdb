import textwrap as tw
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

User = get_user_model()


class Genre(models.Model):
    "Модель жанров."
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        db_index=True
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='slug',
        unique=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Вы используете недопустимые символы'
        )]
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return tw.shorten(self.name, width=15, placeholder='...')


class Category(models.Model):
    "Модель категорий."
    name = models.CharField(
        max_length=256,
        verbose_name='Название категории',
        db_index=True
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='slug',
        unique=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Вы используете недопустимые символы'
        )]
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return tw.shorten(self.name, width=15, placeholder='...')


class Title(models.Model):
    "Модель произведений."
    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения',
        db_index=True
    )
    year = models.PositiveIntegerField(
        verbose_name='Год выпуска',
        validators=[
            MinValueValidator(
                0,
                message='Год выпуска должен быть нашей эры :)'
            ),
            MaxValueValidator(
                int(datetime.now().year),
                message='Год выпуска должен быть не больше текущего'
            )
        ]
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles',
        verbose_name='Жанр произведения'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория произведения',
        null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', 'name')
        constraints = (
            models.UniqueConstraint(
                fields=['year', 'name'],
                name='unique_year_title'
            ),
        )

    def __str__(self):
        return tw.shorten(self.name, width=15, placeholder='...')


class GenreTitle(models.Model):
    "Модель связи жанра и произведения."
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )

    class Meta:
        verbose_name = 'Связь жанра и произведения'
        verbose_name_plural = 'Связи жанров и произведений'
        ordering = ('id',)

    def __str__(self):
        return f'Произведению {self.title} соответствует жанр {self.genre}'


class Review(models.Model):
    "Модель отзывов."
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
        null=True
    )
    text = models.TextField(
        max_length=500,
        help_text='Оставьте свой отзыв на произведение',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    score = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, 'Не меньше 1'),
            MaxValueValidator(10, 'Не больше 10')
        ],
        help_text='Поставьте произведению свою оценку',
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        return tw.shorten(self.text, width=15, placeholder='...')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            ),
        ]


class Comment(models.Model):
    "Модель комментариев."
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(
        max_length=200,
        verbose_name='Комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        return tw.shorten(self.text, width=15, placeholder='...')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
