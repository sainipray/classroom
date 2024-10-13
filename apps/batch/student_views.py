from rest_framework import viewsets
from abstract.views import ReadOnlyCustomResponseMixin
from .models import Batch, Enrollment, BatchPurchaseOrder  # Assuming you have an Enrollment model for student batch enrollments
from .student_serializers import BatchSerializer, RetrieveBatchSerializer  # Create these serializers


class AvailableBatchViewSet(ReadOnlyCustomResponseMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = BatchSerializer
    retrieve_serializer_class = RetrieveBatchSerializer

    def get_queryset(self):
        # Retrieve all Enrollment records for the authenticated user
        enrolled_batch_ids = Enrollment.objects.filter(student=self.request.user).values_list('batch_id', flat=True)

        # Retrieve BatchPurchaseOrder IDs associated with the authenticated user
        purchased_batch_ids = BatchPurchaseOrder.objects.filter(transaction__user=self.request.user).values_list('batch_id', flat=True)

        # Fetch batches that are published and exclude both enrolled and purchased batches
        available_batches = Batch.objects.filter(
            is_published=True  # Ensure this field is present in your Batch model
        ).exclude(
            id__in=enrolled_batch_ids  # Exclude batches the user is already enrolled in
        ).exclude(
            id__in=purchased_batch_ids  # Exclude purchased batches if necessary
        )

        return available_batches


class PurchasedBatchViewSet(ReadOnlyCustomResponseMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = BatchSerializer
    retrieve_serializer_class = RetrieveBatchSerializer

    def get_queryset(self):
        # Retrieve batch IDs for enrolled batches for the authenticated user
        enrolled_batches = Enrollment.objects.filter(student=self.request.user).values_list('batch_id', flat=True)

        # Retrieve batch IDs for purchased batches for the authenticated user
        purchased_batches = BatchPurchaseOrder.objects.filter(transaction__user=self.request.user).values_list('batch_id', flat=True)

        # Combine both lists of batch IDs into a single set
        combined_batch_ids = set(enrolled_batches) | set(purchased_batches)  # Use set to avoid duplicates

        # Return Batch objects corresponding to the combined batch IDs
        return Batch.objects.filter(
            id__in=combined_batch_ids
        ).select_related('created_by').filter(is_published=True)  # Ensure the batches are published
