from django_filters.rest_framework import DjangoFilterBackend

from abstract.views import ReadOnlyCustomResponseMixin
from .models import TestSeries, TestSeriesPurchaseOrder
from .student_serializers import StudentPurchasedTestSeriesSerializer, StudentTestSeriesSerializer


class AvailableTestSeriesViewSet(ReadOnlyCustomResponseMixin):
    """
    ViewSet to get all available test series that a student hasn't purchased.
    """
    queryset = TestSeries.objects.filter(is_published=True)  # Base queryset for available test series
    serializer_class = StudentTestSeriesSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['is_digital']

    def get_queryset(self):
        # purchased_test_series_ids = TestSeriesPurchaseOrder.objects.filter(
        #     student=self.request.user
        # ).values_list('test_series_id', flat=True)

        available_test_series = TestSeries.objects.filter(is_published=True)
        return available_test_series


class PurchasedTestSeriesViewSet(ReadOnlyCustomResponseMixin):
    """
    ViewSet to get all test series that a student has purchased.
    """
    serializer_class = StudentPurchasedTestSeriesSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['is_digital']
    queryset = TestSeries.objects.filter(is_published=True)

    def get_queryset(self):
        purchased_test_series = TestSeriesPurchaseOrder.objects.filter(transaction__user=self.request.user).values_list(
            'test_series_id', flat=True)

        return TestSeries.objects.filter(
            id__in=purchased_test_series
        ).select_related('created_by').filter(is_published=True)
