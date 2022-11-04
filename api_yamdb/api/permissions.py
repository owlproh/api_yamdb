from rest_framework import permissions


class IsOnlyAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.role == 'admin' or request.user.is_superuser
        ) and request.user.is_authenticated


class IsAdminModerAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return (request.user.role == 'admin'
                or request.user.role == 'moderator'
                or request.user == obj.author)


class IsAdminOrAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user
                or request.user.role == 'admin')
