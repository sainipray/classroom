from rest_framework import viewsets

from .models import FreeResource
from .serializers import VideoFreeResourceSerializer, DocumentFreeResourceSerializer


class VideoViewSet(viewsets.ModelViewSet):
    queryset = FreeResource.objects.filter(resource_type=FreeResource.ResourceType.VIDEO)
    serializer_class = VideoFreeResourceSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = FreeResource.objects.filter(resource_type=FreeResource.ResourceType.DOCUMENT)
    serializer_class = DocumentFreeResourceSerializer
