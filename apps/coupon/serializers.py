from rest_framework import serializers

from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.full_name')

    class Meta:
        model = Coupon
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        courses = validated_data.get('courses')
        if courses:
            validated_data['is_all_courses'] = False
        else:
            validated_data['is_all_courses'] = True

        coupon = Coupon.objects.create(created_by=request.user, **validated_data)

        return coupon
