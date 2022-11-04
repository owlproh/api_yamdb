from rest_framework.permissions import (BasePermission,
                                        SAFE_METHODS)

class IsSuperUser(BasePermission):  # проверку на superuser надо отдельно, это всё же не админ, а отдельный тип
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):  # думаю не нужно на уровне объекта ещё проверять
        return request.user.is_authenticated and request.user.is_admin


class IsAuthor(BasePermission):
    def has_permission(self, request, view):    # а это думаю не надо, автор всё же к объекту привязан
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.author == request.user  # на аутентификацию проверку надо бы тоже


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_moderator

    def has_object_permission(self, request, view, obj):  # думаю не нужно на уровне объекта ещё проверять
        return request.user.is_authenticated and request.user.is_moderator


class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):    # думаю не нужно на уровне объекта ещё проверять
        return request.method in SAFE_METHODS
