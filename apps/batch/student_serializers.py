from rest_framework import serializers
from .models import Batch


class BatchSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.full_name')

    class Meta:
        model = Batch
        fields = ['id', 'name', 'batch_code', 'start_date', 'subject', 'live_class_link', 'created_by']


class RetrieveBatchSerializer(BatchSerializer):
    pass
