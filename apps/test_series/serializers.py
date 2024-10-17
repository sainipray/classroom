from rest_framework import serializers
from .models import TestSeries, Highlight, TestSeriesCategory


class TestSeriesCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSeriesCategory
        fields = '__all__'
class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Highlight
        fields = ['id', 'highlight_points']


class TestSeriesSerializer(serializers.ModelSerializer):
    highlights = HighlightSerializer(many=True, required=False)

    class Meta:
        model = TestSeries
        fields = ['id', 'name', 'category', 'total_questions', 'duration', 'price', 'description', 'url', 'highlights']

    def create(self, validated_data):
        highlights_data = validated_data.pop('highlights', [])
        test_series = TestSeries.objects.create(**validated_data)
        for highlight_data in highlights_data:
            Highlight.objects.create(test_series=test_series, **highlight_data)
        return test_series

    def update(self, instance, validated_data):
        highlights_data = validated_data.pop('highlights', [])
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.total_questions = validated_data.get('total_questions', instance.total_questions)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.price = validated_data.get('price', instance.price)
        instance.description = validated_data.get('description', instance.description)
        instance.url = validated_data.get('url', instance.url)
        instance.save()

        # Handle highlights
        if highlights_data:
            instance.highlights.all().delete()  # Remove old highlights
            for highlight_data in highlights_data:
                Highlight.objects.create(test_series=instance, **highlight_data)

        return instance
