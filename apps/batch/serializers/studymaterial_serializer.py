from rest_framework import serializers

from apps.batch.models import StudyMaterial, Batch, LiveClass


# class BatchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Batch
#         fields = '__all__'


# class LiveClassSerializer(serializers.ModelSerializer):
#     # batch = BatchSerializer(read_only=True)
#
#     class Meta:
#         model = LiveClass
#         fields = '__all__'


class StudyMaterialSerializer(serializers.ModelSerializer):
    # batch = BatchSerializer(read_only=True)
    # live_class_recording = LiveClassSerializer(read_only=True)

    class Meta:
        model = StudyMaterial
        fields = '__all__'


class RetrieveStudyMaterialSerializer(serializers.ModelSerializer):
    # batch = BatchSerializer(read_only=True)
    # live_class_recording = LiveClassSerializer(read_only=True)

    class Meta:
        model = StudyMaterial
        fields = '__all__'


class ListStudyMaterialSerializer(serializers.ModelSerializer):
    # batch = BatchSerializer(read_only=True)
    # live_class_recording = LiveClassSerializer(read_only=True)

    class Meta:
        model = StudyMaterial
        fields = '__all__'
