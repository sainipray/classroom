from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .student_views import StudentVideoViewSet, StudentDocumentViewSet
from .views import VideoViewSet, DocumentViewSet

router = DefaultRouter()
router.register(r'videos', VideoViewSet, basename='videos')
router.register(r'documents', DocumentViewSet, basename='documents')

student_router = DefaultRouter()
student_router.register(r'student-videos', StudentVideoViewSet, basename='student_videos')
student_router.register(r'student-documents', StudentDocumentViewSet, basename='student_documents')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(student_router.urls)),
]
