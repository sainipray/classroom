# serializers.py
from rest_framework import serializers

from .models import Course, CourseValidityPeriod, CourseLiveClass


class StudentCourseValidityPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseValidityPeriod
        fields = ['id', 'duration_value', 'duration_unit', 'price', 'discount', 'effective_price', 'is_promoted']


class StudentCourseSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.full_name')
    validity_periods = StudentCourseValidityPeriodSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class RetrieveStudentCourseSerializer(StudentCourseSerializer):
    categories_info = serializers.ReadOnlyField()
    content = serializers.ReadOnlyField()
    validity_periods = StudentCourseValidityPeriodSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class StudentCourseLiveClassSerializer(serializers.ModelSerializer):
    student_join_link = serializers.ReadOnlyField()

    class Meta:
        model = CourseLiveClass
        fields = ('title', 'date', 'class_id', 'status', 'recording_url',
                  'duration', 'recording_status', 'student_join_link')

