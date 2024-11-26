from rest_framework import serializers

from .models import TestSeries, TestSeriesCategory, PhysicalProduct


class TestSeriesCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSeriesCategory
        fields = '__all__'


class PhysicalProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalProduct
        fields = ['delivery_status', 'gst']


class TestSeriesSerializer(serializers.ModelSerializer):
    physical_product = PhysicalProductSerializer(required=False)  # Nested serializer

    class Meta:
        model = TestSeries
        fields = '__all__'
        extra_kwargs = {
            'effective_price': {'read_only': True},  # effective_price is read-only
        }

    def create(self, validated_data):
        physical_product_data = validated_data.pop('physical_product', None)
        validated_data['created_by'] = self.context['request'].user
        test_series = TestSeries.objects.create(**validated_data)
        if physical_product_data:
            PhysicalProduct.objects.create(test_series=test_series, **physical_product_data)

        return test_series

    def update(self, instance, validated_data):
        # Extract physical product data if provided
        physical_product_data = validated_data.pop('physical_product', None)

        # Update TestSeries fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create PhysicalProduct
        if physical_product_data:
            if hasattr(instance, 'physical_product'):
                # Update existing PhysicalProduct
                physical_product = instance.physical_product
                for attr, value in physical_product_data.items():
                    setattr(physical_product, attr, value)
                physical_product.save()
            else:
                # Create PhysicalProduct if it doesn't exist
                PhysicalProduct.objects.create(test_series=instance, **physical_product_data)

        return instance


class RetrieveTestSeriesSerializer(serializers.ModelSerializer):
    category = TestSeriesCategorySerializer(read_only=True)
    physical_product = PhysicalProductSerializer()  # Nested serializer

    class Meta:
        model = TestSeries
        fields = '__all__'
