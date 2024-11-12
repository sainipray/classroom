from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .student_views import StudentFreeResourceViewSet
from .views import FreeResourceViewSet, FolderFileViewSet

router = DefaultRouter()
router.register(r'resources', FreeResourceViewSet, basename='resources')
router.register(r'content', FolderFileViewSet, basename='course-content')

student_router = DefaultRouter()

student_router.register(r'student-resources', StudentFreeResourceViewSet, basename='student_resources')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(student_router.urls)),
]
