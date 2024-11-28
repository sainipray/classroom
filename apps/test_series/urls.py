from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.test_series.student_views import AvailableTestSeriesViewSet, PurchasedTestSeriesViewSet
from apps.test_series.views import TestSeriesViewSet, TestSeriesCategoryViewSet, ProductOrdersViewSet

router = DefaultRouter()
router.register(r'test-series', TestSeriesViewSet)
router.register(r'categories', TestSeriesCategoryViewSet)
router.register(r'product-orders', ProductOrdersViewSet)
student_router = DefaultRouter()
student_router.register(r'student/available-test-series', AvailableTestSeriesViewSet, basename='available-test-series')
student_router.register(r'student/purchased-test-series', PurchasedTestSeriesViewSet, basename='purchased-test-series')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(student_router.urls)),

]
