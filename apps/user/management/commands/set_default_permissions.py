from django.core.management.base import BaseCommand

from apps.user.models import Module, ModulePermission


class Command(BaseCommand):
    help = "Set default permissions for ADMIN, STUDENT, MANAGER, and INSTRUCTOR"

    def handle(self, *args, **options):
        # Define only the modules, no specific permissions in the data
        permissions_data = [
            'Courses', 'Students', 'Fee Record', 'Fee Structure', 'Batches',
            'Coupons', 'Test Portal', 'Lead & Inquiries', 'Test Series',
            'Transactions', 'Free Resource', 'Team Members', 'Report', 'Settings'
        ]

        # Create modules if they don't exist
        for module_name in permissions_data:
            module, created = Module.objects.get_or_create(name=module_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Module {module_name} created"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Module {module_name} already exists"))

        # Default roles to permissions mapping
        default_permissions = {
            'ADMIN': {'can_view': True, 'can_create': True, 'can_edit': True, 'can_delete': True},
            'STUDENT': {'can_view': False, 'can_create': False, 'can_edit': False, 'can_delete': False},
            'MANAGER': {'can_view': True, 'can_create': True, 'can_edit': True, 'can_delete': False},
            'INSTRUCTOR': {'can_view': True, 'can_create': True, 'can_edit': False, 'can_delete': False},
        }

        # Loop through the roles and set permissions for each module
        for module_name in permissions_data:
            for role, permissions in default_permissions.items():
                module = Module.objects.get(name=module_name)
                # Replace existing permissions if they exist
                permission, created = ModulePermission.objects.update_or_create(
                    role=role,
                    module=module,
                    defaults={
                        'can_view': permissions['can_view'],
                        'can_create': permissions['can_create'],
                        'can_edit': permissions['can_edit'],
                        'can_delete': permissions['can_delete'],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created permissions for {role} on {module_name}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Updated permissions for {role} on {module_name}"))

        self.stdout.write(self.style.SUCCESS('Default permissions set successfully'))
