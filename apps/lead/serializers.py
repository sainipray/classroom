from rest_framework import serializers
from .models import Lead

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'


class ListLeadSerializer(serializers.ModelSerializer):
    assign_lead = serializers.ReadOnlyField(source='assign_lead.full_name')

    class Meta:
        model = Lead
        fields = '__all__'
