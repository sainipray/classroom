from rest_framework import serializers

from apps.batch.models import Enrollment, Batch


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'


class EnrollmentSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)
    student = serializers.StringRelatedField()  # Adjust if you need more details
    approved_by = serializers.StringRelatedField()  # Adjust if you need more details

    class Meta:
        model = Enrollment
        fields = '__all__'


class RetrieveEnrollmentSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)
    student = serializers.StringRelatedField()  # Adjust if you need more details
    approved_by = serializers.StringRelatedField()  # Adjust if you need more details

    class Meta:
        model = Enrollment
        fields = '__all__'


class ListEnrollmentSerializer(serializers.ModelSerializer):
    batch = BatchSerializer(read_only=True)
    student = serializers.StringRelatedField()  # Adjust if you need more details
    approved_by = serializers.StringRelatedField()  # Adjust if you need more details

    class Meta:
        model = Enrollment
        fields = '__all__'
