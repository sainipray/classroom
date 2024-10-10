# views.py

from abstract.views import ReadOnlyCustomResponseMixin
from .models import Course, CoursePurchaseOrder
from .student_serializers import RetrieveStudentCourseSerializer, \
    StudentCourseSerializer


class AvailableCourseViewSet(ReadOnlyCustomResponseMixin):
    serializer_class = StudentCourseSerializer
    retrieve_serializer_class = RetrieveStudentCourseSerializer

    def get_queryset(self):
        # Retrieve all CoursePurchaseOrders for the authenticated user
        purchased_course_ids = CoursePurchaseOrder.objects.filter(
            student=self.request.user
        ).values_list('course_id', flat=True)

        # Fetch courses that are published and not in the purchased_course_ids
        return Course.objects.filter(
            is_published=True
        ).exclude(
            id__in=purchased_course_ids
        )


class PurchasedCourseCourseViewSet(ReadOnlyCustomResponseMixin):
    queryset = Course.objects.filter(is_published=True)  # Only fetch published courses for students
    serializer_class = StudentCourseSerializer
    retrieve_serializer_class = RetrieveStudentCourseSerializer

    def get_queryset(self):
        return Course.objects.filter(
            id__in=CoursePurchaseOrder.objects.filter(
                student=self.request.user
            ).values_list('course_id', flat=True)
        ).select_related('created_by').prefetch_related('coupons').filter(is_published=True)
