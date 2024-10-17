from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.test_series.views import TestSeriesViewSet, TestSeriesCategoryViewSet

router = DefaultRouter()
router.register(r'test-series', TestSeriesViewSet)
router.register(r'categories', TestSeriesCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),

]
