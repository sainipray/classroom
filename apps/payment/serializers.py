from django.utils import timezone
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import Transaction
from ..batch.models import Batch, BatchPurchaseOrder
from ..coupon.models import Coupon
from ..course.models import Course


class VerifyPaymentSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField(max_length=255)
    razorpay_payment_id = serializers.CharField(max_length=255)
    razorpay_signature = serializers.CharField(max_length=255)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['transaction_id', 'payment_status', 'created_at', 'updated_at']


class PurchaseCourseSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)

    def validate_course_id(self, value):
        if not Course.objects.filter(id=value, is_published=True).exists():
            raise serializers.ValidationError("Invalid or unpublished course ID.")
        return value

    def validate_coupon_code(self, value):
        if not value:
            return None  # No coupon applied

        try:
            coupon = Coupon.objects.get(code=value, status=True, is_visible=True)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code.")

        # Check if coupon is within the valid date range
        now = timezone.now()
        if coupon.start_datetime and now < coupon.start_datetime:
            raise serializers.ValidationError("Coupon is not yet valid.")
        if not coupon.lifetime and coupon.end_datetime and now > coupon.end_datetime:
            raise serializers.ValidationError("Coupon has expired.")

        # Check max uses
        if coupon.max_uses and coupon.total_applied >= coupon.max_uses:
            raise serializers.ValidationError("Coupon usage limit has been reached.")

        # Check usage per student
        user = self.context['request'].user
        if coupon.usage_per_student:
            user_usage = Transaction.objects.filter(user=user, coupon=coupon).count()
            if user_usage >= coupon.usage_per_student:
                raise serializers.ValidationError("You have reached the maximum usage limit for this coupon.")

        return coupon

    def validate(self, attrs):
        coupon = attrs.get('coupon_code')
        if coupon:
            # Optionally, check if the coupon is applicable to the selected course
            course_id = attrs.get('course_id')
            course = Course.objects.get(id=course_id)
            if coupon.courses.exists() and course not in coupon.courses.all():
                raise serializers.ValidationError("This coupon is not applicable to the selected course.")
        return attrs


class ApplyCouponSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    coupon_code = serializers.CharField(max_length=50)

    def validate_course_id(self, value):
        if not Course.objects.filter(id=value, is_published=True).exists():
            raise serializers.ValidationError("Invalid or unpublished course ID.")
        return value

    def validate_coupon_code(self, value):
        try:
            coupon = Coupon.objects.get(code=value, status=True, is_visible=True)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code.")

        # Check if coupon is within the valid date range
        now = timezone.now()
        if coupon.start_datetime and now < coupon.start_datetime:
            raise serializers.ValidationError("Coupon is not yet valid.")
        if not coupon.lifetime and coupon.end_datetime and now > coupon.end_datetime:
            raise serializers.ValidationError("Coupon has expired.")

        # Check max uses
        if coupon.max_uses and coupon.total_applied >= coupon.max_uses:
            raise serializers.ValidationError("Coupon usage limit has been reached.")

        # Check usage per student
        user = self.context['request'].user
        if coupon.usage_per_student:
            user_usage = Transaction.objects.filter(user=user, coupon=coupon).count()
            if user_usage >= coupon.usage_per_student:
                raise serializers.ValidationError("You have reached the maximum usage limit for this coupon.")

        # Check applicability to the course
        course_id = self.initial_data.get('course_id')
        if course_id:
            course = Course.objects.get(id=course_id)
            if coupon.courses.exists() and course not in coupon.courses.all():
                raise serializers.ValidationError("This coupon is not applicable to the selected course.")

        return coupon

    def validate(self, attrs):
        # Ensure that if a coupon is provided, it's applicable to the selected course
        coupon = attrs.get('coupon_code')
        course_id = attrs.get('course_id')
        if coupon and course_id:
            course = Course.objects.get(id=course_id)
            if coupon.courses.exists() and course not in coupon.courses.all():
                raise serializers.ValidationError("This coupon is not applicable to the selected course.")
        return attrs


class PurchaseBatchSerializer(serializers.Serializer):
    batch_id = serializers.IntegerField()
    installment_number = serializers.IntegerField(required=False)  # Make it optional

    def validate(self, attrs):
        batch_id = attrs.get('batch_id')
        installment_number = attrs.get('installment_number')

        batch = get_object_or_404(Batch, id=batch_id, is_published=True)
        fee_structure = batch.fee_structure

        if not fee_structure:
            raise serializers.ValidationError("Batch does not have a fee structure.")

        if installment_number:
            if installment_number < 1 or installment_number > fee_structure.installments:
                raise serializers.ValidationError("Invalid installment number.")

            # Check if the installment has already been purchased
            if BatchPurchaseOrder.objects.filter(
                student=self.context['request'].user,
                batch=batch,
                installment_number=installment_number
            ).exists():
                raise serializers.ValidationError(f"Installment {installment_number} has already been purchased.")

        attrs['batch'] = batch
        attrs['fee_structure'] = fee_structure
        return attrs

class PayInstallmentSerializer(serializers.Serializer):
    purchase_order_id = serializers.IntegerField()

    def validate(self, attrs):
        purchase_order_id = attrs.get('purchase_order_id')
        user = self.context['request'].user

        purchase_order = get_object_or_404(BatchPurchaseOrder, id=purchase_order_id, student=user)

        if purchase_order.is_paid:
            raise serializers.ValidationError("This installment has already been paid.")

        attrs['purchase_order'] = purchase_order
        return attrs
