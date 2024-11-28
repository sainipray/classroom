from rest_framework import serializers

from .models import TestSeries, TestSeriesCategory


class TestSeriesCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSeriesCategory
        fields = '__all__'


class TestSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSeries
        fields = '__all__'
        extra_kwargs = {
            'effective_price': {'read_only': True},  # effective_price is read-only
        }

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return TestSeries.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Update TestSeries fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class RetrieveTestSeriesSerializer(serializers.ModelSerializer):
    category = TestSeriesCategorySerializer(read_only=True)

    class Meta:
        model = TestSeries
        fields = '__all__'
