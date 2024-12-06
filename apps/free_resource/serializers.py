import os

from django.core.exceptions import ValidationError
from rest_framework import serializers

from apps.free_resource.models import FreeResource, Folder, File


class FreeResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeResource
        fields = '__all__'

    def validate_video_file(self, value):
        if value:
            ext = os.path.splitext(value)[1].lower()
            valid_video_extensions = ['.mp4', '.avi', '.mkv', '.mov']
            if ext not in valid_video_extensions:
                raise ValidationError("Invalid video file type. Allowed types: mp4, avi, mkv, mov.")
        return value

    def create(self, validated_data):
        validated_data['resource_type'] = FreeResource.ResourceType.VIDEO
        return FreeResource.objects.create(**validated_data)



class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['id', 'resource', 'title', 'parent', 'created', 'order']


class FileSerializer(serializers.ModelSerializer):
    title = serializers.CharField(read_only=True)

    class Meta:
        model = File
        fields = ['id', 'title', 'folder', 'url', 'created', 'is_locked', 'order']
