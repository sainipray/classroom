# serializers.py
from rest_framework import serializers
from .models import Course

class StudentCourseSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.full_name')

    class Meta:
        model = Course
        fields = '__all__'


class RetrieveStudentCourseSerializer(StudentCourseSerializer):
    categories_info = serializers.ReadOnlyField()
    content = serializers.ReadOnlyField()
