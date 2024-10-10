from rest_framework import serializers

from apps.batch.models import FeeStructure


class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = ['id', 'structure_name', 'fee_amount', 'installments', 'total_amount']
