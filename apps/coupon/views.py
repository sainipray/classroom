from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from abstract.views import CustomResponseMixin
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if the coupon has already been used
        if instance.total_applied > 0:  # Assuming 'times_used' tracks coupon usage
            raise ValidationError("This coupon has already been used and cannot be modified.")

        # Proceed with the update if the coupon has not been used
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if the coupon has already been used
        if instance.total_applied > 0:  # Assuming 'times_used' tracks coupon usage
            raise ValidationError("This coupon has already been used and cannot be deleted.")

        # Proceed with deletion if the coupon has not been used
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
