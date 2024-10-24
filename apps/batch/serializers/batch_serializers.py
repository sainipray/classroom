from rest_framework import serializers

from apps.batch.models import Batch, Subject, Folder, File
from apps.batch.serializers.fee_serializers import FeeStructureSerializer
from apps.batch.serializers.liveclass_serializers import LiveClassSerializer
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
        fields = ['name', 'start_date', 'subject', 'created_by', 'batch_code', 'fee_structure', 'thumbnail']

    def create(self, validated_data):
        # The validated data doesn't contain `created_by` yet, so we add it manually.
        validated_data['created_by'] = self.context['request'].user
        # Now save the instance
        return super().create(validated_data)


class RetrieveBatchSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    created_by = serializers.ReadOnlyField(source='created_by.full_name')
    total_enrolled_students = serializers.ReadOnlyField()
    enrolled_students = serializers.ReadOnlyField()
    student_join_request = serializers.ReadOnlyField()
    fee_structure = FeeStructureSerializer(read_only=True)
    # TODO filter live class of past one day later
    live_classes = LiveClassSerializer(read_only=True, many=True)

    class Meta:
        model = Batch
        fields = '__all__'


class ListBatchSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    created_by = CustomUserSerializer()

    class Meta:
        model = Batch
        fields = '__all__'


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['id', 'batch', 'title', 'parent', 'created']


class FileSerializer(serializers.ModelSerializer):
    title = serializers.CharField(read_only=True)

    class Meta:
        model = File
        fields = ['id', 'title', 'folder', 'url', 'created']
