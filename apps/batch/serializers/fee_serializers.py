from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.batch.models import FeeStructure, Batch, Enrollment, BatchPurchaseOrder
from apps.payment.utils import final_price_with_other_expenses_and_gst

User = get_user_model()


class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = ['id', 'structure_name', 'fee_amount', 'installments', 'total_amount', 'frequency', 'number_of_values']


class AddFeesRecordSerializer(serializers.Serializer):
    batch = serializers.IntegerField()
    student = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    installment_number = serializers.IntegerField(required=False)
    reference_number = serializers.CharField()

    def validate_batch(self, value):
        try:
            batch = Batch.objects.get(id=value)
            return batch
        except Batch.DoesNotExist:
            serializers.ValidationError("Batch does not exist")

    def validate_student(self, value):
        try:
            student = User.objects.get(id=value)
            return student
        except User.DoesNotExist:
            serializers.ValidationError("Student does not exist")

    def validate(self, attrs):
        student = attrs.get('student')
        batch = attrs.get('batch')
        amount = attrs.get('amount')
        installment_number = attrs.get('installment_number', 1)
        try:
            enrollment = Enrollment.objects.get(student=student, batch=batch)
            if not enrollment.is_approved:
                raise serializers.ValidationError({'batch:': "You need to first approve the student enrollment"})
            attrs['enrollment'] = enrollment
        except Enrollment.DoesNotExist:
            raise serializers.ValidationError({'batch:': "There is no pending enrollment for student,"
                                                         " Student should be approved for enrollment"})

        original_price = batch.fee_structure.fee_amount
        final_price_responses = final_price_with_other_expenses_and_gst(original_price)
        if final_price_responses['total_amount'] != amount:
            raise serializers.ValidationError({
                'amount': f"The amount is required for batch installment is {final_price_responses['total_amount']} not matching"
            })

        try:
            batch_purchased = BatchPurchaseOrder.objects.get(
                student=student,
                batch=batch,
                installment_number=installment_number,
            )
            if batch_purchased.is_paid:
                raise serializers.ValidationError({'batch:': "Student already paid amount for this installment"})
            attrs['batch_purchased'] = batch_purchased
        except BatchPurchaseOrder.DoesNotExist:
            # TODO check pervious installment exist or not
            batch_purchased = BatchPurchaseOrder.objects.create(
                student=student,
                batch=batch,
                installment_number=installment_number,
                amount=amount
            )
            attrs['batch_purchased'] = batch_purchased

        return attrs
