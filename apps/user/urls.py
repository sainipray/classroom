# accounts/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .student_views import StudentProfileViewSet
from .views import (
    LoginAPIView,
    PhoneOTPVerifyAPIView,
    RegisterAPIView,
    UserProfileAPIView, StudentViewSet, UserViewSet, PermissionView, PermissionsForRoles,
)

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'users', UserViewSet, basename='user-modification')

student_router = DefaultRouter()
student_router.register(r'my-profile', StudentProfileViewSet)

urlpatterns = [
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("signup/", RegisterAPIView.as_view(), name="signup"),
    path("verify-otp/", PhoneOTPVerifyAPIView.as_view(), name="verify_otp"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("profile/", UserProfileAPIView.as_view(), name="profile"),
    path("user-permissions/", PermissionView.as_view(), name="user_permissions"),
    path("roles-permissions/", PermissionsForRoles.as_view(), name="roles_permissions"),

    # path('users/<int:pk>/', UserUpdateView.as_view(), name='user-update'),
]

urlpatterns += [
    path('', include(router.urls)),
    path('', include(student_router.urls)),
]
