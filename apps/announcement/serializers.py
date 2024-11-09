from rest_framework import serializers

from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'message', 'is_global', 'batch', 'course', 'created', 'modified', 'created_by']
        read_only_fields = ['created_by']

    def create(self, validated_data):
        # Set the created_by field to the user from the request context
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
