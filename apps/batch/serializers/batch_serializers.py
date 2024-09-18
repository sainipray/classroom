from rest_framework import serializers

from apps.batch.models import Batch, Subject
from apps.user.serializers import CustomUserSerializer


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'


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
