from rest_framework import serializers
from .models import Coupon

class CouponSerializer(serializers.ModelSerializer):

    class Meta:
        model = Coupon
        fields = '__all__'  # Specify fields if you need to limit them
