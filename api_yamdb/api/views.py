import uuid

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title

from .permissions import (IsAdminModerAuthor, IsAdminOrAuthor,
                          IsAdminUserOrReadOnly, IsOnlyAdmin)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleSerializer, TokenSerializer, UserMeSerializer,
                          UsersSerializer)

User = get_user_model()


class SignUpAPIView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        try:
            user, create = User.objects.get_or_create(
                email=email,
                username=username
            )
        except Exception:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        confirmation_code = str(uuid.uuid4)
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


class TokenAPIView(APIView):
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data['username']
        confirmation_code = serializer.data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        token = str(AccessToken.for_user(user))
        content = {'token': token}
        return Response(content, status=status.HTTP_201_CREATED)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (permissions.IsAuthenticated, IsOnlyAdmin)
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('username',)
    search_fields = ('username',)
    lookup_field = 'username'

    def perform_create(self, serializer):
        serializer = UsersSerializer(data=self.request.data)
        serializer.is_valid()
        serializer.save()
        return super().perform_create(serializer)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me'
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


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Viewset для объектов модели Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """Viewset для объектов модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    """Viewset для объектов модели Title."""
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAdminUserOrReadOnly,)


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
