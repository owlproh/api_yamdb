import textwrap as tw

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    title = models.ForeignKey(
        'Titles',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
        null=False
    )
    text = models.TextField(
        max_length=500,
        help_text='Оставьте свой отзыв на произведение',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
        null=False
    )
    score = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, 'Не меньше 1'),
            MaxValueValidator(10, 'Не больше 10')
        ],
        help_text='Поставьте произведению свою оценку',
        verbose_name='Оценка',
        null=False
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


class Comment(models.Model):
    title = models.ForeignKey(
        'Titles',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Произведение',
        null=False
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
        null=False
    )
    text = models.TextField(
        max_length=300,
        verbose_name='Комментарий',
        null=False
    )
    author = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        null=False
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
