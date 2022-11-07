from rest_framework import permissions


class IsOnlyAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_admin or request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        return (request.user.is_admin or request.user.is_staff)


class IsAdminModerAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
<<<<<<< HEAD
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
=======
            obj.author == request.user
>>>>>>> parent of ecc2873 (53 passed)
            or request.user.is_moderator
            or request.user.is_admin
        )


class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.is_admin
        return False


class IsAdminOrAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.user == obj.author or request.user.is_admin)
