from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Permissions for users with is_admin = True
    """

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)