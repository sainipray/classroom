from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from .models import FreeResource
from .student_serializers import StudentFreeResourceSerializer


class StudentFreeResourceViewSet(mixins.ListModelMixin,
                                 GenericViewSet):
    queryset = FreeResource.objects.all()
    serializer_class = StudentFreeResourceSerializer
