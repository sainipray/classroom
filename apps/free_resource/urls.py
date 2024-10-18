from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import  VideoViewSet, DocumentViewSet

router = DefaultRouter()
router.register(r'videos', VideoViewSet, basename='videos')
router.register(r'documents', DocumentViewSet, basename='documents')

urlpatterns = [
    path('', include(router.urls)),
]
