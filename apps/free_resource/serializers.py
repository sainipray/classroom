import os

from django.core.exceptions import ValidationError
from rest_framework import serializers

from apps.free_resource.models import FreeResource


class VideoFreeResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeResource
        fields = ('video_file', 'title', 'thumbnail')

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

class DocumentFreeResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeResource
        fields = ('document_file', 'title', 'thumbnail')

    def validate_document_file(self, value):
        if value:
            ext = os.path.splitext(value)[1].lower()
            valid_document_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx']
            if ext not in valid_document_extensions:
                raise ValidationError("Invalid document file type. Allowed types: pdf, doc, docx, ppt, pptx.")
        return value

    def create(self, validated_data):
        validated_data['resource_type'] = FreeResource.ResourceType.DOCUMENT
        return FreeResource.objects.create(**validated_data)
