# views.py

from abstract.views import ReadOnlyCustomResponseMixin
from .models import Course
from .student_serializers import RetrieveStudentCourseSerializer, \
    StudentCourseSerializer


class StudentCourseViewSet(ReadOnlyCustomResponseMixin):
    queryset = Course.objects.filter(is_published=True)  # Only fetch published courses for students
    serializer_class = StudentCourseSerializer
    retrieve_serializer_class = RetrieveStudentCourseSerializer


class StudentPurchaseCourseViewSet(ReadOnlyCustomResponseMixin):
    queryset = Course.objects.filter(is_published=True)  # Only fetch published courses for students
    serializer_class = StudentCourseSerializer
    retrieve_serializer_class = RetrieveStudentCourseSerializer
