from rest_framework.permissions import BasePermission

from apps.user.models import Roles


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_staff and request.user.role == Roles.ADMIN
        )


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Roles.STUDENT


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Roles.INSTRUCTOR
