from rest_framework import viewsets

from abstract.views import ReadOnlyCustomResponseMixin
from .models import Batch, Enrollment  # Assuming you have an Enrollment model for student batch enrollments
from .student_serializers import BatchSerializer, RetrieveBatchSerializer  # Create these serializers


class AvailableBatchViewSet(ReadOnlyCustomResponseMixin):
    serializer_class = BatchSerializer
    retrieve_serializer_class = RetrieveBatchSerializer

    def get_queryset(self):
        # Retrieve all Enrollment records for the authenticated user
        enrolled_batch_ids = Enrollment.objects.filter(student=self.request.user).values_list('batch_id', flat=True)

        # Fetch batches that are published and not in the enrolled_batch_ids
        return Batch.objects.filter(
            is_published=True  # Make sure to have this field in your Batch model if necessary
        ).exclude(
            id__in=enrolled_batch_ids
        )


class PurchasedBatchViewSet(ReadOnlyCustomResponseMixin):
    serializer_class = BatchSerializer
    retrieve_serializer_class = RetrieveBatchSerializer

    def get_queryset(self):
        return Batch.objects.filter(
            id__in=Enrollment.objects.filter(student=self.request.user).values_list('batch_id', flat=True)
        ).select_related('created_by').filter(is_published=True)
