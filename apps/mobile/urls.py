from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.mobile.views import BannerViewSet, StudentBannerViewSet

router = DefaultRouter()
router.register(r'banners', BannerViewSet)

student_router = DefaultRouter()
student_router.register(r'student-banners', StudentBannerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(student_router.urls))
]
