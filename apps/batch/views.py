from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from abstract.views import CustomResponseMixin
from .models import Subject, Batch, Enrollment, LiveClass, Attendance, StudyMaterial
from .serializers.attendance_serializers import AttendanceSerializer
from .serializers.batch_serializers import BatchSerializer, RetrieveBatchSerializer, SubjectSerializer
from .serializers.enrollment_serializers import EnrollmentSerializer, BatchStudentUserSerializer
from .serializers.liveclass_serializers import LiveClassSerializer
from .serializers.studymaterial_serializer import StudyMaterialSerializer


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


class EnrollmentViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    queryset = Enrollment.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollments = serializer.save()
        return Response({"enrollments": [enrollment.id for enrollment in enrollments]}, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        enrollment = self.get_object()
        enrollment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='add-student')
    def add_student(self, request):
        student_serializer = BatchStudentUserSerializer(data=request.data)
        student_serializer.is_valid(raise_exception=True)

        # Create the student and enroll them
        user = student_serializer.save()
        return Response({"user_id": user.id, "message": "Student created and enrolled."},
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        try:
            enrollment = self.get_object()
            enrollment.is_approved = True
            enrollment.approved_by = request.user  # Assuming you want to set the user who approved
            enrollment.save()
            return Response({"message": "Enrollment approved."}, status=status.HTTP_200_OK)
        except Enrollment.DoesNotExist:
            return Response({"error": "Enrollment not found."}, status=status.HTTP_404_NOT_FOUND)


class LiveClassViewSet(viewsets.ModelViewSet):
    queryset = LiveClass.objects.all()
    serializer_class = LiveClassSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer


class StudyMaterialViewSet(viewsets.ModelViewSet):
    queryset = StudyMaterial.objects.all()
    serializer_class = StudyMaterialSerializer
