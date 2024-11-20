from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from abstract.views import ReadOnlyCustomResponseMixin
from .models import Batch, Enrollment, \
    BatchPurchaseOrder, LiveClass, Attendance  # Assuming you have an Enrollment model for student batch enrollments
from .student_serializers import StudentBatchSerializer, StudentRetrieveBatchSerializer, \
    StudentLiveClassSerializer, StudentAttendanceSerializer, generate_offline_classes  # Create these serializers


class AbstractBatchStudentView:

    def get_available_batches(self):
        # Retrieve all Enrollment records for the authenticated user
        enrolled_batch_ids = Enrollment.objects.filter(student=self.request.user, is_approved=True).values_list(
            'batch_id', flat=True)

        # Retrieve BatchPurchaseOrder IDs associated with the authenticated user
        purchased_batch_ids = BatchPurchaseOrder.objects.filter(transaction__user=self.request.user).values_list(
            'batch_id', flat=True)

        # Fetch batches that are published and exclude both enrolled and purchased batches
        available_batches = Batch.objects.filter(
            is_published=True  # Ensure this field is present in your Batch model
        ).exclude(
            id__in=enrolled_batch_ids  # Exclude batches the user is already enrolled in
        ).exclude(
            id__in=purchased_batch_ids  # Exclude purchased batches if necessary
        )
        return available_batches

    def get_purchased_batches(self):
        # Retrieve batch IDs for enrolled batches for the authenticated user
        enrolled_batches = Enrollment.objects.filter(student=self.request.user, is_approved=True).values_list(
            'batch_id', flat=True)

        # Retrieve batch IDs for purchased batches for the authenticated user
        purchased_batches = BatchPurchaseOrder.objects.filter(transaction__user=self.request.user).values_list(
            'batch_id', flat=True)

        # Combine both lists of batch IDs into a single set
        combined_batch_ids = set(enrolled_batches) | set(purchased_batches)  # Use set to avoid duplicates

        # Return Batch objects corresponding to the combined batch IDs
        return Batch.objects.filter(
            id__in=combined_batch_ids
        ).select_related('created_by').filter(is_published=True)  # Ensure the batches are published


class AvailableBatchViewSet(AbstractBatchStudentView, ReadOnlyCustomResponseMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentBatchSerializer
    retrieve_serializer_class = StudentRetrieveBatchSerializer

    def get_queryset(self):
        return self.get_available_batches()


class PurchasedBatchViewSet(AbstractBatchStudentView, ReadOnlyCustomResponseMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentBatchSerializer
    retrieve_serializer_class = StudentRetrieveBatchSerializer

    def get_queryset(self):
        return self.get_purchased_batches()


class StudentLiveClassesViewSet(mixins.ListModelMixin,
                                GenericViewSet):
    serializer_class = StudentLiveClassSerializer
    queryset = LiveClass.objects.all()

    def get_queryset(self):
        # TODO check current user have batch access
        batch = Batch.objects.get(id=self.kwargs['batch'])
        live_classes = batch.live_classes.all()
        return live_classes


class StudentBatchAttendanceViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = StudentAttendanceSerializer
    queryset = Attendance.objects.all()

    def get_queryset(self):
        # TODO check current user have batch access
        batch = Batch.objects.get(id=self.kwargs['batch'])
        user = self.request.user
        return Attendance.objects.filter(student=user, live_class__batch=batch)


class StudentFeesRecordAPI(ListAPIView):
    def get(self, request, *args, **kwargs):
        now = timezone.now()
        unpaid_fees = []
        upcoming_fees = []
        paid_fees = []
        # 1. Fetch all BatchPurchaseOrders marked as paid
        paid_fees_data = BatchPurchaseOrder.objects.filter(is_paid=True, student=self.request.user).annotate(
            total_paid=Sum('amount'))

        for data in paid_fees_data:
            paid_fees.append({
                'amount': data.total_paid,
                'batch': StudentBatchSerializer(data.batch).data,
                'batch_name': data.batch.name,
                'payment_date': data.payment_date,
                'installment_number': data.installment_number,
            })

        # 2. Fetch approved enrollments with a batch, student, and batch_joined_date
        enrollments = Enrollment.objects.filter(is_approved=True, student=self.request.user).select_related(
            'batch__fee_structure', 'student'
        )

        for enrollment in enrollments:
            batch = enrollment.batch
            fee_structure = batch.fee_structure
            if not fee_structure:
                continue  # Skip if there's no fee structure

            # Get frequency, number_of_values, and installments
            frequency = fee_structure.frequency
            interval = fee_structure.number_of_values
            num_installments = fee_structure.installments
            fee_amount = fee_structure.fee_amount
            join_date = enrollment.batch_joined_date

            # Define date increment based on frequency and number_of_values
            if frequency == 'weekly':
                date_increment = timedelta(weeks=interval)
            elif frequency == 'monthly':
                date_increment = relativedelta(months=interval)
            else:
                date_increment = relativedelta(months=1)  # Default to monthly if frequency is unknown

            for installment_num in range(1, num_installments + 1):
                due_date = join_date + (installment_num - 1) * date_increment

                # Check if a corresponding BatchPurchaseOrder already exists
                order_exists = BatchPurchaseOrder.objects.filter(
                    student=self.request.user,
                    batch=batch,
                    installment_number=installment_num,
                ).exists()

                if order_exists:
                    continue  # Skip if BatchPurchaseOrder record already exists

                # Categorize based on due date and payment status
                record = {
                    'batch_name': batch.name,
                    'batch': StudentBatchSerializer(batch).data,
                    'installment_number': installment_num,
                    'amount': fee_amount,
                    'due_date': due_date,
                }

                if due_date < now:
                    # Past-due unpaid installment
                    unpaid_fees.append(record)
                else:
                    # Upcoming installment
                    upcoming_fees.append(record)

        # Structure response with grouped data
        response_data = {
            'paid_fees': paid_fees,
            'unpaid_fees': unpaid_fees,
            'upcoming_fees': upcoming_fees,
        }

        return Response(response_data)


class StudentBatchClassesView(AbstractBatchStudentView, APIView):
    def get(self, request, *args, **kwargs):
        main_live_classes = []
        main_offline_classes = []
        for batch in self.get_purchased_batches():
            live_classes = batch.live_classes.all()
            live_classes_data = StudentLiveClassSerializer(live_classes, many=True).data
            offline_class = generate_offline_classes(batch)

            main_live_classes.extend(live_classes_data)
            main_offline_classes.extend(offline_class)

        data = {
            'live_classes': main_live_classes,
            'offline_classes': main_offline_classes
        }
        return Response(data)
