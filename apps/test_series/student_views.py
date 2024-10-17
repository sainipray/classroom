from rest_framework import viewsets

from .models import TestSeries, TestSeriesPurchaseOrder
from .student_serializers import StudentPurchasedTestSeriesSerializer, StudentTestSeriesSerializer


class AvailableTestSeriesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to get all available test series that a student hasn't purchased.
    """
    serializer_class = StudentTestSeriesSerializer

    def get_queryset(self):
        purchased_test_series_ids = TestSeriesPurchaseOrder.objects.filter(
            student=self.request.user
        ).values_list('test_series_id', flat=True)

        available_test_series = TestSeries.objects.filter(is_published=True).exclude(id__in=purchased_test_series_ids)
        return available_test_series


class PurchasedTestSeriesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to get all test series that a student has purchased.
    """
    serializer_class = StudentPurchasedTestSeriesSerializer

    def get_queryset(self):
        purchased_test_series = TestSeriesPurchaseOrder.objects.filter(transaction__user=self.request.user).values_list(
            'test_series_id', flat=True)

        return TestSeries.objects.filter(
            id__in=purchased_test_series
        ).select_related('created_by').filter(is_published=True)
