from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from .models import Subject, Batch, Enrollment, LiveClass, Attendance, StudyMaterial
from .serializers.attendance_serializers import AttendanceSerializer
from .serializers.batch_serializers import BatchSerializer, RetrieveBatchSerializer, SubjectSerializer
from .serializers.enrollment_serializers import EnrollmentSerializer
from .serializers.liveclass_serializers import LiveClassSerializer
from .serializers.studymaterial_serializer import StudyMaterialSerializer


class CustomResponseMixin(viewsets.ModelViewSet):
    list_serializer_class = None
    retrieve_serializer_class = None

    def get_serializer_class(self):
        """ Custom class to update action wise response """
        assert self.serializer_class is not None, (
                "'%s' should either include a `serializer_class` attribute, "
                "or override the `get_serializer_class()` method."
                % self.__class__.__name__
        )
        if self.action in ['create', 'update', 'delete'] and self.serializer_class:
            return self.serializer_class
        if self.action in ['retrieve', ] and self.retrieve_serializer_class:
            return self.retrieve_serializer_class
        if self.action in ['list'] and self.list_serializer_class:
            return self.list_serializer_class
        return self.serializer_class


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('name', 'description',)


class BatchViewSet(CustomResponseMixin):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    retrieve_serializer_class = RetrieveBatchSerializer
    list_serializer_class = RetrieveBatchSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_201_CREATED, data={'message': "Successfully created"})


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer


class LiveClassViewSet(viewsets.ModelViewSet):
    queryset = LiveClass.objects.all()
    serializer_class = LiveClassSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer


class StudyMaterialViewSet(viewsets.ModelViewSet):
    queryset = StudyMaterial.objects.all()
    serializer_class = StudyMaterialSerializer
