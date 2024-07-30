# accounts/urls.py

from django.urls import path

from .views import (
    LoginAPIView,
    PhoneOTPVerifyAPIView,
    RegisterAPIView,
    StudentProfileAPIView,
)

urlpatterns = [
    path("signup/", RegisterAPIView.as_view(), name="signup"),
    path("verify-otp/", PhoneOTPVerifyAPIView.as_view(), name="verify_otp"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("profile/", StudentProfileAPIView.as_view(), name="profile"),
]
