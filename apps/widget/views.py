from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import views, status
from rest_framework.response import Response

from apps.batch.models import Batch, BatchPurchaseOrder, Enrollment
from apps.course.models import Course, CoursePurchaseOrder
from apps.course.serializers import ListCourseSerializer
from apps.user.models import CustomUser, Roles  # Adjust the import based on your project structure


class UserMetricsView(views.APIView):

    def get(self, request, *args, **kwargs):
        # Calculate the metrics
        total_users = CustomUser.objects.exclude(role=Roles.STUDENT).count()
        active_users = CustomUser.objects.exclude(role=Roles.STUDENT).filter(is_active=True).count()
        new_enrollments_last_week = CustomUser.objects.exclude(role=Roles.STUDENT).filter(
            date_joined__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()
        total_instructor = CustomUser.objects.filter(role=Roles.INSTRUCTOR).count()

        # Prepare the response data
        response_data = {
            "total_users": total_users,
            "active_users": active_users,
            "new_enrollments_last_week": new_enrollments_last_week,
            "total_instructor": total_instructor,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class StudentMetricsView(views.APIView):

    def get(self, request, *args, **kwargs):
        # Calculate the metrics
        total_students = CustomUser.objects.filter(role=Roles.STUDENT).count()
        active_students = CustomUser.objects.filter(role=Roles.STUDENT, is_active=True).count()
        new_enrollments_last_week = CustomUser.objects.filter(
            role=Roles.STUDENT,
            date_joined__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()
        inactive_students = CustomUser.objects.filter(role=Roles.STUDENT, is_active=False).count()

        # Prepare the response data
        response_data = {
            "total_students": total_students,
            "active_students": active_students,
            "new_enrollments_last_week": new_enrollments_last_week,
            "inactive_students": inactive_students,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class GlobalMetricsView(views.APIView):

    def get(self, request, *args, **kwargs):
        # Calculate metrics
        total_students = CustomUser.objects.filter(role=Roles.STUDENT).count()  # Total number of students
        total_courses = Course.objects.count()  # Total number of courses
        total_batches = Batch.objects.count()  # Total number of batches

        trending_courses = (
            Course.objects.filter(is_published=True)  # Filter published courses
            .annotate(purchase_count=Count('coursepurchaseorder'))  # Count purchases
            .order_by('-purchase_count', '-created')[:6]  # Order by purchase count and then created date
        )
        serializer = ListCourseSerializer(trending_courses, many=True)
        # Prepare the response data
        response_data = {
            "total_students": total_students,
            "total_courses": total_courses,
            "total_batches": total_batches,
            'trending_courses': serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class FeesMetricsView(views.APIView):
    def get(self, request, *args, **kwargs):
        total_paid_fees = 0
        total_outstanding_fees = 0
        total_records = 0
        purchase_orders = BatchPurchaseOrder.objects.all()
        for order in purchase_orders:
            batch = order.batch
            paid_fees = BatchPurchaseOrder.objects.filter(batch=batch, student=order.student, is_paid=True).aggregate(
                total_paid=Sum('amount'))['total_paid'] or 0
            total_fees = batch.fee_structure.total_amount if batch.fee_structure else 0
            outstanding_fees = total_fees - paid_fees

            total_paid_fees += paid_fees
            total_outstanding_fees += outstanding_fees
            total_records += 1

        response_data = {
            'total_paid_fees': total_paid_fees,
            'total_outstanding_fees': total_outstanding_fees,
            'total_records': total_records
        }
        return Response(response_data, status=status.HTTP_200_OK)


class StudentDashBoardMetricView(views.APIView):

    def get(self, request):
        # Available Batches
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
        ).count()

        # available Course
        purchased_course_ids = CoursePurchaseOrder.objects.filter(
            student=self.request.user
        ).values_list('course_id', flat=True)

        # Fetch courses that are published and not in the purchased_course_ids
        available_courses = Course.objects.filter(
            is_published=True
        ).exclude(
            id__in=purchased_course_ids
        ).count()

        # Enrolled Course
        enrolled_courses = Course.objects.filter(
            id__in=CoursePurchaseOrder.objects.filter(
                student=self.request.user
            ).values_list('course_id', flat=True)
        ).filter(is_published=True).count()

        # Enrolled Batched
        enrolled_batches = Enrollment.objects.filter(student=self.request.user, is_approved=True).values_list(
            'batch_id', flat=True)

        # Retrieve batch IDs for purchased batches for the authenticated user
        purchased_batches = BatchPurchaseOrder.objects.filter(transaction__user=self.request.user).values_list(
            'batch_id', flat=True)

        # Combine both lists of batch IDs into a single set
        combined_batch_ids = set(enrolled_batches) | set(purchased_batches)  # Use set to avoid duplicates

        # Return Batch objects corresponding to the combined batch IDs
        enrolled_batches = Batch.objects.filter(
            id__in=combined_batch_ids
        ).select_related('created_by').filter(is_published=True).count()  # Ensure the batches are published

        response_data = {
            'available_batches': available_batches,
            'available_courses': available_courses,
            'enrolled_courses': enrolled_courses,
            'enrolled_batches': enrolled_batches,
        }
        return Response(response_data, status=status.HTTP_200_OK)
