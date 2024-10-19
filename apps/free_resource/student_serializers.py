from rest_framework import serializers

from apps.free_resource.models import FreeResource


class StudentVideoFreeResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeResource
        fields = ('video_file', 'title', 'thumbnail', 'link', 'id')


class StudentDocumentFreeResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeResource
        fields = ('document_file', 'title', 'thumbnail', 'link', 'id')
