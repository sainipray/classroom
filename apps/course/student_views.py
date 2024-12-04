# views.py
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from abstract.views import ReadOnlyCustomResponseMixin
from .models import Course, CoursePurchaseOrder, CourseLiveClass
from .student_serializers import RetrieveStudentCourseSerializer, \
    StudentCourseSerializer, StudentCourseLiveClassSerializer


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
        ).filter(is_published=True)


class StudentCourseLiveClassesViewSet(mixins.ListModelMixin,
                                      GenericViewSet):
    serializer_class = StudentCourseLiveClassSerializer
    queryset = CourseLiveClass.objects.all()

    def get_queryset(self):
        # TODO check current user have course access
        course = Course.objects.get(id=self.kwargs['course'])
        live_classes = course.live_classes.all()
        return live_classes
