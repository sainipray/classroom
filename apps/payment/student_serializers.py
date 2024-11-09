from rest_framework import serializers

from apps.payment.models import Transaction


class StudentTransactionSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField()
    content_name = serializers.ReadOnlyField()

    class Meta:
        model = Transaction
        fields = '__all__'
