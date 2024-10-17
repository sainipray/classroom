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
        # Update all fields, including highlights
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.price = validated_data.get('price', instance.price)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.description = validated_data.get('description', instance.description)
        instance.url = validated_data.get('url', instance.url)
        instance.highlights = validated_data.get('highlights', instance.highlights)
        instance.thumbnail = validated_data.get('thumbnail', instance.thumbnail)
        instance.is_published = validated_data.get('is_published', instance.is_published)
        instance.save()

        return instance


class RetrieveTestSeriesSerializer(serializers.ModelSerializer):
    category = TestSeriesCategorySerializer(read_only=True)

    class Meta:
        model = TestSeries
        fields = '__all__'
