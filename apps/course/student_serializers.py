# serializers.py
from rest_framework import serializers

from .models import Course, CourseValidityPeriod


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
