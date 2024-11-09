from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .student_views import StudentAnnouncementViewSet
from .views import AnnouncementViewSet

router = DefaultRouter()
router.register(r'announcements', AnnouncementViewSet, basename="announcements")
router.register(r'student-announcements', StudentAnnouncementViewSet, basename="student-announcements")

urlpatterns = [
    path('', include(router.urls)),
]
