from django.contrib import admin

from .models import Comment, Review


class CommentInLine(admin.StackedInline):
    model = Comment


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'title', 'text', 'author', 'score', 'pub_date'
    )
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    inlines = [CommentInLine]
