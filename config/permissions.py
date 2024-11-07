from rest_framework.permissions import BasePermission

from apps.user.models import Roles

from rest_framework.permissions import BasePermission

from apps.user.models import Roles, ModulePermission, Module


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


class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        user_role = request.user.role  # Assuming `role` is a field in the user model

        # Automatically grant access to 'STUDENT' role (if no permission checks required)
        if user_role == Roles.STUDENT:
            return True  # Skip permission checks

        module_name = view.kwargs.get('module')
        permission = ModulePermission.objects.filter(
            role=user_role,
            module__name=module_name
        ).first()

        if not permission:
            return False

        # Check permissions for specific actions
        if request.method == 'GET' and permission.can_view:
            return True
        elif request.method == 'POST' and permission.can_create:
            return True
        elif request.method == 'PUT' and permission.can_edit:
            return True
        elif request.method == 'DELETE' and permission.can_delete:
            return True

        return False


def create_permissions_for_role(role_name):
    # Skip permission creation for the 'STUDENT' role
    if role_name == Roles.STUDENT:
        return

    modules = Module.objects.all()

    for module in modules:
        ModulePermission.objects.get_or_create(
            module=module,
            role=role_name,
            defaults={
                'can_view': False,
                'can_create': False,
                'can_edit': False,
                'can_delete': False,
            }
        )
