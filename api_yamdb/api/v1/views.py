from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title
from users.models import User

from .filters import TitleFilter
from .mixins import MasterViewSet
from .permissions import (IsAdminModerAuthor, IsAdminOrSuper,
                          IsAdminUserOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          ConfirmationCodeSerializer, GenreSerializer,
                          ReviewSerializer, SignUpSerializer,
                          TitleReadSerializer, TitleSerializer,
                          UserMeSerializer, UsersSerializer)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def sign_up(request):
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        user, create = User.objects.get_or_create(
            email=email,
            username=username
        )
        confirmation_code = default_token_generator.make_token(user)
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            'Введите код для продолжения регистрации',
            confirmation_code,
            'admin@gmail.com',
            [email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def getting_token(request):
    serializer = ConfirmationCodeSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if not default_token_generator.check_token(user, confirmation_code):
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
    token = str(AccessToken.for_user(user))
    content = {'token': token}
    return Response(content, status=status.HTTP_201_CREATED)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminOrSuper,)
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('username',)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = UserMeSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserMeSerializer(user,
                                          data=request.data,
                                          partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(MasterViewSet):
    """Viewset для объектов модели Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(
        methods=['DELETE'],
        detail=False,
        url_path=r'(?P<slug>[-a-zA-Z0-9_]+)',
        url_name='delete_category'
    )
    def delete_category(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(MasterViewSet):
    """Viewset для объектов модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    @action(
        methods=['DELETE'],
        detail=False,
        url_path=r'(?P<slug>[-a-zA-Z0-9_]+)',
        url_name='delete_genre'
    )
    def delete_genre(self, request, slug):
        genre = get_object_or_404(Genre, slug=slug)
        genre.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TitleViewSet(viewsets.ModelViewSet):
    """Viewset для объектов модели Title."""
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_serializer_method(self):
        if self.request.method == 'GET':
            return TitleReadSerializer
        return TitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для объектов модели Comment."""
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModerAuthor,)

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для объектов модели Review."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModerAuthor,)

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user, title=self.get_title())
