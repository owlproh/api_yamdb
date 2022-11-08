from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
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


class ConfirmationCodeSerializer(serializers.Serializer):
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


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор объектов модели Title при GET запросах."""
    genre = GenreSerializer(
        many=True,
        read_only=True
    )
    category = CategorySerializer(
        read_only=True
    )
    rating = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
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
            'name',
            'year',
            'description',
            'genre',
            'category')
        validators = [
            UniqueTogetherValidator(
                queryset=Title.objects.all(),
                fields=('year', 'name'),
                message='Произведение, вышедшее в указанном'
                        'году уже есть в базе'
            )
        ]

    def to_representation(self, title):
        serializer = TitleReadSerializer(title)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    author = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        fields = (
            'id',
            'text',
            'author',
            'pub_date'
        )
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    author = serializers.StringRelatedField(
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
        model = Review

    def validate(self, data):
        """Не даёт плодить комментарии."""
        if self.context['request'].method != 'POST':
            return data
        user = self.context['request'].user
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        if Review.objects.filter(author=user, title__id=title_id).exists():
            raise serializers.ValidationError('Вы уже оставили отзыв.')
        return data
