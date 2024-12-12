from rest_framework import serializers

from apps.batch.models import Batch, Subject
from apps.course.models import Course, Category, CourseCategorySubCategory
from apps.test_series.models import TestSeries


class PublicTestSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSeries
        fields = '__all__'


class PublicCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PublicCategorySubCategorySerializer(serializers.ModelSerializer):
    category = PublicCategorySerializer(read_only=True)

    class Meta:
        model = CourseCategorySubCategory
        fields = '__all__'


class PublicCourseSerializer(serializers.ModelSerializer):
    categories_subcategories = PublicCategorySubCategorySerializer(many=True)

    class Meta:
        model = Course
        fields = '__all__'


class PublicBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'


class PublicSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
