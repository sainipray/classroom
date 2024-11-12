from rest_framework import serializers

from apps.free_resource.models import FreeResource


class StudentFreeResourceSerializer(serializers.ModelSerializer):
    content = serializers.ReadOnlyField()

    class Meta:
        model = FreeResource
        fields = '__all__'


