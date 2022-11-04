import uuid

from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title
from users.models import User

from .permissions import IsAdminModerAuthor, IsAdminOrAuthor, IsOnlyAdmin
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleSerializer, TokenSerializer, UserMeSerializer,
                          UsersSerializer)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """Viewset для объектов модели Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """Viewset для объектов модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    """Viewset для объектов модели Title."""
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для лбъектов модели Comment."""
    serializer_class = CommentSerializer
   # permission_classes = pass

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
   # permission_classes = pass

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user, title=self.get_title())


class SignUpAPIView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid()
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        try:
            user, create = User.objects.get_or_create(
                email=email,
                username=username
            )
        except Exception:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
        serializer.is_valid()
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        token = AccessToken.for_user(user)
        content = {'token': token}
        return Response(content, status=status.HTTP_201_CREATED)


class UsersViewSet(viewsets.ModelViewSet):
    """ViewSet для объектов модели User."""
    queryset = User.object.all()
    serializer_class = UsersSerializer
    permission_classes = (IsOnlyAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class UserMeView(mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    serializer_class = UserMeSerializer
    permission_classes = (IsAdminOrAuthor,)

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return user
