from rest_framework import serializers

from apps.batch.models import Batch, Subject
from apps.course.models import Course, Category
from apps.test_series.models import TestSeries


class PublicTestSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSeries
        fields = '__all__'


class PublicCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class PublicBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'


class PublicCategorySerializer(serializers.Serializer):
    class Meta:
        model = Category
        fields = '__all__'


class PublicSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
