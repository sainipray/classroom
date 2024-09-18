from rest_framework import serializers

from apps.batch.models import LiveClass, Batch


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'


class LiveClassSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)

    class Meta:
        model = LiveClass
        fields = '__all__'


class RetreiveLiveClassSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)

    class Meta:
        model = LiveClass
        fields = '__all__'


class ListLiveClassSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)

    class Meta:
        model = LiveClass
        fields = '__all__'
