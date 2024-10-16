from datetime import datetime, timedelta

import pytz
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from abstract.views import CustomResponseMixin
from config.live_video import MeritHubAPI
from .models import Subject, Batch, Enrollment, LiveClass, Attendance, StudyMaterial, FeeStructure, Folder, File
from .serializers.attendance_serializers import AttendanceSerializer
from .serializers.batch_serializers import BatchSerializer, RetrieveBatchSerializer, SubjectSerializer, \
    FolderSerializer, FileSerializer
from .serializers.enrollment_serializers import EnrollmentSerializer, BatchStudentUserSerializer, \
    ListEnrollmentSerializer
from .serializers.fee_serializers import FeeStructureSerializer
from .serializers.liveclass_serializers import LiveClassSerializer, RetrieveLiveClassSerializer
from .serializers.studymaterial_serializer import StudyMaterialSerializer
from ..utils.functions import merge_and_sort_items


class SubjectViewSet(CustomResponseMixin):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('name', 'description',)


class BatchViewSet(CustomResponseMixin):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    retrieve_serializer_class = RetrieveBatchSerializer
    list_serializer_class = RetrieveBatchSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('name',)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_201_CREATED, data={'message': "Successfully created"})

    @action(detail=True, methods=['patch'])
    def toggle_publish(self, request, pk=None):
        try:
            batch = self.get_object()  # Get the batch object by ID
            batch.is_published = not batch.is_published  # Toggle the is_published field
            batch.save()  # Save the updated object
            return Response(
                {'message': f"Batch {'published' if batch.is_published else 'unpublished'} successfully."},
                status=status.HTTP_200_OK
            )
        except Batch.DoesNotExist:
            return Response({'error': 'Batch not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='create-folder')
    def create_folder(self, request, pk=None):
        batch = self.get_object()
        request.data['batch'] = batch.id  # Set the batch ID
        serializer = FolderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='folders/(?P<folder_id>[^/.]+)/create-file')
    def create_file(self, request, pk, folder_id=None):
        # If no folder_id is provided, default to the root (Home) folder
        if folder_id is None:
            # Get or create the Home folder
            home_folder, created = Folder.objects.get_or_create(title='Home', batch=self.get_object())
            folder = home_folder
        else:
            folder = Folder.objects.get(id=folder_id)  # Fetch the folder

        request.data['folder'] = folder.id  # Set the folder ID
        serializer = FileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def build_breadcrumb(self, folder):
        breadcrumb = []
        current_folder = folder
        while current_folder is not None:
            breadcrumb.append({'id': current_folder.id, 'title': current_folder.title})
            current_folder = current_folder.parent  # Traverse up to the parent folder

        # Reverse the breadcrumb list to have the root folder at the start
        breadcrumb.reverse()
        return breadcrumb

    @action(detail=True, methods=['get'], url_path='folder-structure')
    def get_folder_structure(self, request, pk=None):
        batch = self.get_object()
        folder_id = request.query_params.get('folder_id')  # Get folder ID from query parameters

        if folder_id:
            try:
                folder = Folder.objects.get(id=folder_id, batch=batch)
            except Folder.DoesNotExist:
                return Response({'detail': 'Folder not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Get files (files) of the current folder
            files = File.objects.filter(folder=folder).order_by('created')
            file_serializer = FileSerializer(files, many=True)

            # Get immediate subfolders
            subfolders = Folder.objects.filter(parent=folder).order_by('created')
            subfolder_serializer = FolderSerializer(subfolders, many=True)

            # Use the utility function to merge and sort
            merged_structure = merge_and_sort_items(subfolder_serializer.data, file_serializer.data)
            breadcrumb = self.build_breadcrumb(folder)

            folder_structure = {
                'id': folder.id,
                'title': folder.title,
                'items': merged_structure
            }
        else:
            # If no folder_id is provided, return the root folder structure
            root_folder, _ = Folder.objects.get_or_create(batch=batch, parent__isnull=True, title='Home')

            # Get files (files) of the current folder
            file_serializer = FileSerializer(root_folder.files.all(), many=True)

            # Get immediate subfolders
            subfolder_serializer = FolderSerializer(root_folder.folders.all(), many=True)

            # Use the utility function to merge and sort
            merged_structure = merge_and_sort_items(subfolder_serializer.data, file_serializer.data)
            breadcrumb = [{'id': root_folder.id, 'title': root_folder.title}]

            folder_structure = {
                'id': root_folder.id,
                'title': root_folder.title,
                'items': merged_structure
            }

        return Response({'batch_id': batch.id, 'folder_structure': folder_structure, 'breadcrumb': breadcrumb},
                        status=status.HTTP_200_OK)



class EnrollmentViewSet(CustomResponseMixin):
    serializer_class = EnrollmentSerializer
    queryset = Enrollment.objects.all()
    list_serializer_class = ListEnrollmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        enrollments = serializer.save()
        return Response({"enrollments": [enrollment.id for enrollment in enrollments]}, status=status.HTTP_201_CREATED)

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

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        try:
            enrollment = self.get_object()
            enrollment.delete()  # Delete the enrollment request
            return Response({"message": "Enrollment request rejected."}, status=status.HTTP_204_NO_CONTENT)
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


class CreateLiveClassView(APIView):

    def post(self, request):
        batch_id = request.data.get("batch_id")
        title = request.data.get("title")

        if not batch_id or not title:
            return Response({"error": "Batch ID and title are required."}, status=status.HTTP_400_BAD_REQUEST)
            # Get current time and set end time to one hour later
        # Get the current time in UTC
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)

        # Set start time and end time
        start_time = now_utc.isoformat()  # Current time in UTC
        end_time = (now_utc + timedelta(hours=1)).isoformat()  # One hour later in UTC

        # Set other fields to default values
        duration = 60  # Default duration
        lang = "en"  # Default language
        time_zone_id = "Asia/Kolkata"  # Default time zone
        description = "This is a scheduled class."  # Default description
        access = "private"  # Default access
        recording = {
            "record": True,
            "autoRecord": False,
            "recordingControl": True
        }
        participant_control = {
            "write": False,
            "audio": False,
            "video": False
        }
        schedule = []  # Set your default schedule if necessary
        total_classes = 1  # Default total classes

        # Get the batch object
        batch = get_object_or_404(Batch, id=batch_id)

        # Assuming you have configured your client ID and secret key in settings
        client_id = "cqb8fh1nuvta0dldbsdg"
        secret_key = "$2a$04$fQ7kQ1or4UnWWC76vtFPKeovH3CJNWHiQTcJH03VuEJvpX7VDWENW"
        api = MeritHubAPI(client_id, secret_key)

        # Prepare the class data
        class_data = {
            "title": title,
            "startTime": start_time,
            "endDate": end_time,
            "duration": duration,
            "lang": lang,
            "timeZoneId": time_zone_id,
            "description": description,
            "type": "oneTime",  # or "perma" based on your logic
            "access": access,
            "login": False,  # Change if necessary
            "layout": "CR",  # Change as needed
            "status": "up",  # Change if necessary
            "recording": recording,
            "participantControl": participant_control,
            "schedule": schedule,
            "totalClasses": total_classes,
        }

        # Schedule the class (assumes you have a user_id for the teacher)
        live_class = api.schedule_class(user_id=self.request.user.id, class_data=class_data, batch=batch)
        serializer = RetrieveLiveClassSerializer(instance=live_class)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FeeStructureViewSet(CustomResponseMixin):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
