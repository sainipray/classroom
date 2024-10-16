from django.utils import timezone
from rest_framework import views, status
from rest_framework.response import Response

from apps.batch.models import Batch
from apps.course.models import Course
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
        # Check if the user is an admin
        if not request.user.is_staff:  # Adjust this check as per your user permission model
            return Response({"detail": "You do not have permission to access this resource."},
                            status=status.HTTP_403_FORBIDDEN)

        # Calculate metrics
        total_students = CustomUser.objects.filter(role=Roles.STUDENT).count()  # Total number of students
        total_courses = Course.objects.count()  # Total number of courses
        total_batches = Batch.objects.count()  # Total number of batches

        # Prepare the response data
        response_data = {
            "total_students": total_students,
            "total_courses": total_courses,
            "total_batches": total_batches,
        }

        return Response(response_data, status=status.HTTP_200_OK)
