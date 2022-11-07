from django.contrib import admin

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User

per_page: int = 10


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug'
    )
    list_per_page = per_page
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug'
    )
    list_per_page = per_page
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'year',
        'description',
        'category'
    )
    list_per_page = per_page
    list_filter = ('name',)
    search_fields = ('name', 'year', 'category')
    empty_value_display = '-пусто-'


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'genre',
        'title'
    )
    empty_value_display = '-пусто-'
    list_filter = ('genre',)
    list_per_page = per_page
    search_fields = ('title',)


class CommentInLine(admin.StackedInline):
    model = Comment


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'text',
        'author',
        'score',
        'pub_date'
    )
    list_filter = ('author', 'score', 'pub_date')
    search_fields = ('author',)
    list_per_page = per_page
    empty_value_display = '-пусто-'
    inlines = [CommentInLine]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role'
    )
    list_per_page = per_page
    list_filter = ('username', 'first_name', 'last_name', 'role')
    search_fields = ('username', 'role')