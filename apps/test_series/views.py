from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from abstract.views import CustomResponseMixin
from .models import TestSeries, TestSeriesCategory
from .serializers import TestSeriesSerializer, TestSeriesCategorySerializer


class TestSeriesCategoryViewSet(CustomResponseMixin):
    queryset = TestSeriesCategory.objects.all()
    serializer_class = TestSeriesCategorySerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('title',)


class TestSeriesViewSet(CustomResponseMixin):
    queryset = TestSeries.objects.all()
    serializer_class = TestSeriesSerializer
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
