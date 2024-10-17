from rest_framework import serializers

from .models import TestSeries, TestSeriesPurchaseOrder, TestSeriesCategory


class TestSeriesStudentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSeriesCategory
        fields = '__all__'


class StudentTestSeriesSerializer(serializers.ModelSerializer):
    category = TestSeriesStudentCategorySerializer(read_only=True)

    class Meta:
        model = TestSeries
        fields = '__all__'


class StudentPurchasedTestSeriesSerializer(serializers.ModelSerializer):
    category = TestSeriesStudentCategorySerializer(read_only=True)

    class Meta:
        model = TestSeries
        fields = '__all__'
