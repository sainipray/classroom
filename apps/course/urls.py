from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.course.views import CategoryViewSet, SubcategoryViewSet, CourseViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubcategoryViewSet)
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),
]
