from rest_framework import serializers

from .models import Announcement
from ..batch.models import Batch
from ..course.models import Course


class StudentAnnouncementBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ('id', 'name',)


class StudentAnnouncementCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'name',)


class StudentAnnouncementSerializer(serializers.ModelSerializer):
    batch = StudentAnnouncementBatchSerializer(read_only=True)
    course = StudentAnnouncementCourseSerializer(read_only=True)
    created_by = serializers.ReadOnlyField(source='created_by.full_name')

    class Meta:
        model = Announcement
        fields = '__all__'
