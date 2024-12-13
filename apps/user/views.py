# accounts/views.py

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from push_notifications.models import GCMDevice
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from abstract.views import CustomResponseMixin
from config.sms.textlocal import LOGIN_OTP_KEY, SIGNUP_OTP_KEY, SMSManager
from .models import CustomUser, Roles, ModulePermission, Module
from .schema_definitions import (
    login_api_view,
    phone_otp_verify_api_view,
    register_api_view,
)
from .serializers import (
    LoginSerializer,
    SignupSerializer,
    UserProfileSerializer,
    VerifyOTPSerializer, CustomUserSerializer, StudentSerializer, StudentUserSerializer, ResendOTPSerializer,
)


class BaseSendOTPAPIView(generics.GenericAPIView):
    def send_otp(self, data, otp_key):
        phone_number = data["phone_number"]
        user = data["user"]
        otp_manager = SMSManager(user)
        data = otp_manager.send_otp(str(phone_number), otp_key)
        return data["token"]


class RegisterAPIView(BaseSendOTPAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    @register_api_view
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {"user": user, "phone_number": user.phone_number}
        reference_key = self.send_otp(data, SIGNUP_OTP_KEY)
        return Response(
            {
                "message": "Please verify OTP sent to your phone number",
                "reference_key": reference_key,
            },
            status=status.HTTP_200_OK,
        )


class PhoneOTPVerifyAPIView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = ()

    @phone_otp_verify_api_view
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        user = CustomUser.objects.get(phone_number=phone_number)
        user.is_active = True
        user.last_login = timezone.now()
        user.save()

        token = serializer.validated_data.get('registration_id')
        device_id = serializer.validated_data.get("device_id")

        if token and device_id:
            # Deactivate or delete any existing device for the user
            GCMDevice.objects.filter(user=user).delete()

            # Register the new device
            device = GCMDevice.objects.create(
                user=user,
                registration_id=token,
                name=f"{user.full_name}'s Device",
                active=True
            )

        data = {}
        refresh = RefreshToken.for_user(user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data["message"] = "Phone verified"
        data["role"] = user.role
        # data["user"] = self.get_user_serializer_data(user)
        return Response(data)


class ResendOTPAPIView(BaseSendOTPAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ResendOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        data = {"user": user, "phone_number": user.phone_number}
        reference_key = self.send_otp(data, LOGIN_OTP_KEY)
        return Response(
            {
                "message": "OTP resent to your phone number",
                "reference_key": reference_key,
            },
            status=status.HTTP_200_OK,
        )


class LoginAPIView(BaseSendOTPAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    @login_api_view
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        user = CustomUser.objects.get(phone_number=phone_number)
        data = {"user": user, "phone_number": phone_number}
        reference_key = self.send_otp(data, LOGIN_OTP_KEY)
        return Response(
            {
                "message": "OTP sent to your phone number",
                "reference_key": reference_key,
            },
            status=status.HTTP_200_OK,
        )


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class UserViewSet(CustomResponseMixin):
    queryset = CustomUser.objects.exclude(role=Roles.STUDENT)
    serializer_class = CustomUserSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('full_name', 'email', 'phone_number')
    filterset_fields = ['role']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class StudentViewSet(CustomResponseMixin):
    queryset = CustomUser.objects.filter(role=Roles.STUDENT).exclude(student__isnull=True)
    serializer_class = StudentUserSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('full_name', 'email', 'phone_number')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "Student information Created"}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        student = instance.student
        serializer = StudentSerializer(student, data=request.data, partial=partial)
        user_serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True) and user_serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        self.perform_update(user_serializer)
        return Response({"message": "Student information Updated"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        student = self.get_object()  # Get the student user instance
        student.is_active = not student.is_active  # Toggle active status
        student.save()  # Save the changes

        status_message = "activated" if student.is_active else "deactivated"
        return Response({"message": f"Student account has been {status_message}."}, status=status.HTTP_200_OK)


class PermissionView(APIView):

    def get(self, request):
        # Get the role of the currently authenticated user
        user_role = request.user.role  # Assuming 'role' is a field in the user model

        # Retrieve all modules
        modules = Module.objects.all()

        # Default permissions for certain roles
        if user_role == Roles.ADMIN:
            # ADMIN role has full permissions for all modules
            permissions_data = [{
                'module': module.name,
                'view': True,
                'create': True,
                'edit': True,
                'delete': True
            } for module in modules]
            return Response(permissions_data)

        elif user_role == Roles.STUDENT:
            # STUDENT role has no permissions for any module
            permissions_data = [{
                'module': module.name,
                'view': False,
                'create': False,
                'edit': False,
                'delete': False
            } for module in modules]
            return Response(permissions_data)

        # For roles like MANAGER or INSTRUCTOR, fetch permissions from the database
        permissions = ModulePermission.objects.filter(role=user_role)

        # Create a dictionary to map modules to permissions
        permission_dict = {perm.module.name: perm for perm in permissions}

        # Prepare the response data for all modules
        permissions_data = []

        for module in modules:
            # Get permissions for this module, or set default if no permission exists for the role
            perm = permission_dict.get(module.name)

            if perm:
                permissions_data.append({
                    'module': module.name,
                    'view': perm.can_view,
                    'create': perm.can_create,
                    'edit': perm.can_edit,
                    'delete': perm.can_delete
                })
            else:
                # If no permission is found for the role, default to no permissions
                permissions_data.append({
                    'module': module.name,
                    'view': False,
                    'create': False,
                    'edit': False,
                    'delete': False
                })

        return Response(permissions_data)


class PermissionsForRoles(APIView):

    def get(self, request):
        # Get permissions for Manager and Instructor
        roles = [Roles.MANAGER, Roles.INSTRUCTOR]  # We can extend this to include other roles if needed

        permissions_data = {}

        for role in roles:
            permissions = ModulePermission.objects.filter(
                role=role)  # Assuming 'role' is the related field in ModulePermission

            permissions_data[role] = []
            for perm in permissions:
                permissions_data[role].append({
                    'module': perm.module.name,  # Assuming 'module' has a 'name' field
                    'view': perm.can_view,
                    'create': perm.can_create,
                    'edit': perm.can_edit,
                    'delete': perm.can_delete
                })

        return Response(permissions_data)

    def post(self, request):
        """
        Save permissions for Manager and Instructor roles
        """
        data = request.data
        roles = [Roles.MANAGER, Roles.INSTRUCTOR]

        # Iterate through each role and update the permissions
        for role in roles:
            if role not in data:
                raise ValidationError(f"Missing data for role: {role}")

            for perm_data in data[role]:
                module_name = perm_data.get('module')
                try:
                    module_permission = ModulePermission.objects.get(role=role, module__name=module_name)
                except ModulePermission.DoesNotExist:
                    # If the permission does not exist, create a new one
                    module_permission = ModulePermission(role=role, module_name=module_name)

                # Update permission values
                module_permission.can_view = perm_data.get('view', module_permission.can_view)
                module_permission.can_create = perm_data.get('create', module_permission.can_create)
                module_permission.can_edit = perm_data.get('edit', module_permission.can_edit)
                module_permission.can_delete = perm_data.get('delete', module_permission.can_delete)

                # Save the updated permission object
                module_permission.save()

        return Response({"message": "Permissions updated successfully."}, status=status.HTTP_200_OK)
