from rest_framework.permissions import BasePermission


class IsAgent(BasePermission):
    """Allow any authenticated user (agents, supervisors, admins)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsSupervisor(BasePermission):
    """Allow only supervisors and admins."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_supervisor_or_above())


class IsAdminUser(BasePermission):
    """Allow only admin-role users."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, 'role', None) == 'admin')
