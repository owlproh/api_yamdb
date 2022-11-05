from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        fields = ('username', 'email')

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError('Недопустимый логин!')
        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields = ('username', 'confirmation_code')


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class UserMeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = (
            'name',
            'slug'
        )


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = (
            'name',
            'slug'
        )


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title."""
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category'
        )


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = (
            'id',
            'text',
            'author',
            'pub_date'
        )
        read_only_fields = (
            'id',
            'author',
            'pub_date'
        )
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date'
        )
        read_only_fields = (
            'id',
            'author',
            'pub_date'
        )
        model = Review

    def validate(self, data):
        """Не даёт плодить комментарии."""
        if self.context('request').method == 'POST':
            user = self.context('request').user
            title_id = self.context('view').kwargs.get('title_id')
            title = get_object_or_404(Title, pk=title_id)
            if Review.objects.filter(author=user, title=title).exists():
                raise serializers.ValidationError('Вы уже оставили отзыв.')
        return data
