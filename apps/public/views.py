from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny

from abstract.views import ReadOnlyCustomResponseMixin
from apps.batch.models import Batch, Subject
from apps.course.models import Course, Category
from apps.public.serializers import PublicTestSeriesSerializer, PublicCourseSerializer, PublicBatchSerializer, \
    PublicCategorySerializer, PublicSubjectSerializer
from apps.test_series.models import TestSeries


class PublicCategoryViewSet(ReadOnlyCustomResponseMixin):
    serializer_class = PublicCategorySerializer
    queryset = Category.objects.filter(status=1)
    permission_classes = [AllowAny]


class PublicSubjectViewSet(ReadOnlyCustomResponseMixin):
    serializer_class = PublicSubjectSerializer
    queryset = Subject.objects.filter(is_active=True)
    permission_classes = [AllowAny]


class PublicTestSeriesViewSet(ReadOnlyCustomResponseMixin):
    queryset = TestSeries.objects.filter(is_published=True)
    serializer_class = PublicTestSeriesSerializer
    permission_classes = [AllowAny]


class PublicCourseViewSet(ReadOnlyCustomResponseMixin):
    queryset = Course.objects.all()
    serializer_class = PublicCourseSerializer
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('name',)


class PublicBatchViewSet(ReadOnlyCustomResponseMixin):
    queryset = Batch.objects.all()
    serializer_class = PublicBatchSerializer
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('name',)
