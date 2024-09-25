from rest_framework import serializers

from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.full_name')

    class Meta:
        model = Coupon
        # fields = '__all__'  # Specify fields if you need to limit them
        exclude = ('courses',)

    def create(self, validated_data):
        request = self.context.get('request')
        coupon = Coupon.objects.create(created_by=request.user, **validated_data)

        return coupon
