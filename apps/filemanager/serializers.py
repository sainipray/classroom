from rest_framework import serializers

from .models import File, Folder


class FolderSerializer(serializers.ModelSerializer):
    subfolders = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    files = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ["id", "name", "parent", "owner", "subfolders", "files"]


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["id", "name", "file", "folder", "owner"]
