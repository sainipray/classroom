# accounts/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LoginAPIView,
    PhoneOTPVerifyAPIView,
    RegisterAPIView,
    StudentProfileAPIView, UserCreateListView, StudentViewSet,
)

router = DefaultRouter()
router.register(r'students', StudentViewSet)
urlpatterns = [
    path("signup/", RegisterAPIView.as_view(), name="signup"),
    path("verify-otp/", PhoneOTPVerifyAPIView.as_view(), name="verify_otp"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("profile/", StudentProfileAPIView.as_view(), name="profile"),
    path('users/', UserCreateListView.as_view(), name='user-list-create'),

    # path('users/<int:pk>/', UserUpdateView.as_view(), name='user-update'),
]

urlpatterns += [
    path('', include(router.urls)),
]
