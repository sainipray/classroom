# accounts/views.py

from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import CustomUser, Roles
from .student_serializers import StudentUserProfileSerializer, StudentProfileSerializer


class StudentProfileViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    queryset = CustomUser.objects.filter(role=Roles.STUDENT).exclude(student__isnull=True)
    serializer_class = StudentUserProfileSerializer

    def get_object(self):
        return self.request.user

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        student = instance.student
        serializer = StudentProfileSerializer(student, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        for attr, value in serializer.validated_data.items():
            setattr(student, attr, value)
        student.save()
        return Response({"message": "Student information Updated"}, status=status.HTTP_200_OK)
