from rest_framework import serializers

from apps.batch.models import Batch, Subject
from apps.user.serializers import CustomUserSerializer


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class BatchSerializer(serializers.ModelSerializer):
    # Make created_by read-only as it will be automatically set by the view
    created_by = serializers.ReadOnlyField()
    batch_code = serializers.ReadOnlyField()

    class Meta:
        model = Batch
        fields = ['name', 'start_date', 'subject', 'created_by', 'batch_code']  # Only these fields are exposed

    def create(self, validated_data):
        # The validated data doesn't contain `created_by` yet, so we add it manually.
        validated_data['created_by'] = self.context['request'].user
        # Now save the instance
        return super().create(validated_data)


class RetrieveBatchSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    created_by = CustomUserSerializer()

    class Meta:
        model = Batch
        fields = '__all__'


class ListBatchSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    created_by = CustomUserSerializer()

    class Meta:
        model = Batch
        fields = '__all__'
