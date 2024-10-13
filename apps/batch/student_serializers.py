from rest_framework import serializers

from .models import Batch
from .serializers.fee_serializers import FeeStructureSerializer


class BatchSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.full_name')
    fee_structure = FeeStructureSerializer(read_only=True)
    subject = serializers.ReadOnlyField(source='subject.name')
    installment_details = serializers.SerializerMethodField()
    class Meta:
        model = Batch
        fields = ['id', 'name', 'batch_code', 'start_date', 'subject', 'live_class_link',
                  'created_by', 'fee_structure', 'installment_details']

    def get_installment_details(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            return obj.get_installment_details_for_user(user)
        return []

class RetrieveBatchSerializer(BatchSerializer):
    pass
