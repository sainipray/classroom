# accounts/views.py

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from abstract.views import CustomResponseMixin
from config.sms.textlocal import LOGIN_OTP_KEY, SIGNUP_OTP_KEY, SMSManager
from .models import CustomUser, Roles
from .schema_definitions import (
    login_api_view,
    phone_otp_verify_api_view,
    register_api_view,
)
from .serializers import (
    LoginSerializer,
    SignupSerializer,
    UserProfileSerializer,
    VerifyOTPSerializer, CustomUserSerializer, StudentSerializer, StudentUserSerializer,
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
        # push_notification_token = serializer.validated_data.get("push_notification_token")
        # device_id = serializer.validated_data.get("device_id")
        # remove existing device with same device_id
        user = CustomUser.objects.get(phone_number=phone_number)
        user.is_active = True
        user.last_login = timezone.now()
        user.save()
        # if push_notification_token and device_id:
        #     GCMDevice.objects.filter(name=device_id).delete()
        #     GCMDevice.objects.create(
        #         registration_id=push_notification_token,
        #         name=device_id,
        #         cloud_message_type="FCM",
        #         user=user,
        #     )
        data = {}
        refresh = RefreshToken.for_user(user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data["message"] = "Phone verified"
        data["role"] = user.role
        # data["user"] = self.get_user_serializer_data(user)
        return Response(data)


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class StudentViewSet(viewsets.ModelViewSet):
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
