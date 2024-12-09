from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.public.views import (PublicTestSeriesViewSet, PublicCourseViewSet,
                               PublicBatchViewSet, PublicSubjectViewSet, PublicCategoryViewSet)

router = DefaultRouter()
router.register(r'category', PublicCategoryViewSet)
router.register(r'subject', PublicSubjectViewSet)
router.register(r'test-series', PublicTestSeriesViewSet)
router.register(r'course', PublicCourseViewSet)
router.register(r'batch', PublicBatchViewSet)

urlpatterns = [
    path('', include(router.urls)),

]
