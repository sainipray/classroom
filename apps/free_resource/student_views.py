from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from .models import FreeResource
from .student_serializers import StudentVideoFreeResourceSerializer, StudentDocumentFreeResourceSerializer


class StudentVideoViewSet(mixins.ListModelMixin,
                          GenericViewSet):
    queryset = FreeResource.objects.filter(resource_type=FreeResource.ResourceType.VIDEO)
    serializer_class = StudentVideoFreeResourceSerializer


class StudentDocumentViewSet(mixins.ListModelMixin,
                             GenericViewSet):
    queryset = FreeResource.objects.filter(resource_type=FreeResource.ResourceType.DOCUMENT)
    serializer_class = StudentDocumentFreeResourceSerializer
