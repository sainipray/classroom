from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from abstract.views import CustomResponseMixin
from config.razor_payment import RazorpayService
from .models import Coupon
from .serializers import CouponSerializer


class CouponViewSet(CustomResponseMixin):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

