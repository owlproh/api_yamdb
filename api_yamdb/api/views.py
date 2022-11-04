import uuid

from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView
from rest_framework import mixins, status, viewsets

from users.models import User
from .permissions import IsAdminModerAuthor, IsOnlyAdmin, IsAdminOrAuthor
from .serializers import (SignUpSerializer, TokenSerializer, UsersSerializer, UserMeSerializer)


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
    queryset = User.object.all()
    serializer_class = UsersSerializer
    permission_classes = (IsOnlyAdmin,)


class UserMeView(mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    serializer_class = UserMeSerializer
    permission_classes = (IsAdminOrAuthor,)

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return user
