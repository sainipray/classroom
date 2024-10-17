from django.db.models import Count
from django.utils import timezone
from rest_framework import views, status
from rest_framework.response import Response

from apps.batch.models import Batch
from apps.course.models import Course
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
        inactive_users = CustomUser.objects.exclude(role=Roles.STUDENT).filter(is_active=False).count()

        # Prepare the response data
        response_data = {
            "total_users": total_users,
            "active_users": active_users,
            "new_enrollments_last_week": new_enrollments_last_week,
            "inactive_users": inactive_users,
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
