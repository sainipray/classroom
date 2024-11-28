from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from abstract.views import CustomResponseMixin, ReadOnlyCustomResponseMixin
from .models import TestSeries, TestSeriesCategory, PhysicalProductOrder
from .serializers import TestSeriesSerializer, TestSeriesCategorySerializer, RetrieveTestSeriesSerializer, \
    ProductOrdersSerializer


class TestSeriesCategoryViewSet(CustomResponseMixin):
    queryset = TestSeriesCategory.objects.all()
    serializer_class = TestSeriesCategorySerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('title',)


class TestSeriesViewSet(CustomResponseMixin):
    queryset = TestSeries.objects.all()
    serializer_class = TestSeriesSerializer
    retrieve_serializer_class = RetrieveTestSeriesSerializer
    list_serializer_class = RetrieveTestSeriesSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('name',)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductOrdersViewSet(ReadOnlyCustomResponseMixin):
    queryset = PhysicalProductOrder.objects.all()
    serializer_class = ProductOrdersSerializer
    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """
        Update the delivery status of a PhysicalProductOrder.
        """
        try:
            order = self.get_object()
        except PhysicalProductOrder.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validate the new status
        new_status = request.data.get("delivery_status")
        if new_status not in PhysicalProductOrder.DeliveryStatus.values:
            return Response(
                {"error": f"Invalid status. Allowed values are: {', '.join(PhysicalProductOrder.DeliveryStatus.values)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update the delivery status
        order.delivery_status = new_status
        order.save()

        return Response(
            {"message": "Delivery status updated successfully.", "delivery_status": order.delivery_status},
            status=status.HTTP_200_OK,
        )
