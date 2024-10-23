from django.contrib.auth import get_user_model
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from abstract.views import CustomResponseMixin
from config.live_video import MeritHubAPI
from .models import Subject, Batch, Enrollment, LiveClass, Attendance, StudyMaterial, FeeStructure, Folder, File, \
    BatchPurchaseOrder
from .serializers.attendance_serializers import AttendanceSerializer
from .serializers.batch_serializers import BatchSerializer, RetrieveBatchSerializer, SubjectSerializer, \
    FolderSerializer, FileSerializer
from .serializers.enrollment_serializers import EnrollmentSerializer, BatchStudentUserSerializer, \
    ListEnrollmentSerializer
from .serializers.fee_serializers import FeeStructureSerializer
from .serializers.liveclass_serializers import LiveClassSerializer, RetrieveLiveClassSerializer, \
    CreateLiveClassSerializer
from .serializers.studymaterial_serializer import StudyMaterialSerializer
from ..utils.functions import merge_and_sort_items

User = get_user_model()


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
        student_serializer = BatchStudentUserSerializer(data=request.data, context={'request': request})
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


class LiveClassViewSet(mixins.DestroyModelMixin,
                       GenericViewSet):
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
        serializer = CreateLiveClassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated data
        validated_data = serializer.validated_data
        batch = validated_data['batch']

        # Assuming you have configured your client ID and secret key in settings
        client_id = "cqb8fh1nuvta0dldbsdg"
        secret_key = "$2a$04$fQ7kQ1or4UnWWC76vtFPKeovH3CJNWHiQTcJH03VuEJvpX7VDWENW"
        api = MeritHubAPI(client_id, secret_key)

        # Prepare the class data
        class_data = {
            'title': validated_data['title'],
            'startTime': validated_data['startTime'],
            'endDate': validated_data['endDate'],
            'duration': validated_data['duration'],
            'lang': validated_data['lang'],
            'timeZoneId': validated_data['timeZoneId'],
            'description': validated_data['description'],
            'type': validated_data['type'],
            'access': validated_data['access'],
            'login': validated_data['login'],
            'layout': validated_data['layout'],
            'status': validated_data['status'],
            'recording': validated_data['recording'],
            'participantControl': validated_data['participantControl']
        }
        try:
            live_class = api.schedule_class(
                user_id=self.request.user.id,
                class_data=class_data,
                batch=batch
            )
            enrolled_students = Enrollment.objects.filter(batch=batch, is_approved=True)
            students = []
            for student in enrolled_students:
                user = student.student
                if not user.merit_user_id:
                    response = api.create_user({
                        'name': user.full_name,
                        'email': user.email,
                        'clientUserId': str(user.id),
                        "role": "M",
                        "timeZone": "Asia/Kolkata",
                        "permission": "CJ"
                    })
                    user.merit_user_id = response['userId']
                    user.save()
                common_participant_link = live_class.common_participant_link
                user_link = ""
                if common_participant_link:
                    user_link = common_participant_link.split('/')[-1]
                students.append({
                    "userId": user.merit_user_id,
                    "userLink": user_link,
                    "userType": "su"
                })
            # Now add users in live class
            response = api.add_students_to_class(class_id=live_class.class_id, users=students)
            for student in response:
                try:
                    user = User.objects.get(merit_user_id=student['userId'])
                    live_class_link = api.generate_url(student['userLink'])
                    Attendance.objects.create(student=user, live_class=live_class, live_class_link=live_class_link)
                except User.DoesNotExist:
                    print(f"User {student['userId']}")

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Serialize the created class (assuming you have a serializer for this)
        retrieve_serializer = RetrieveLiveClassSerializer(instance=live_class)
        return Response(retrieve_serializer.data, status=status.HTTP_201_CREATED)


class FeeStructureViewSet(CustomResponseMixin):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer


class FeesRecordAPI(ListAPIView):

    def get(self, request, *args, **kwargs):
        purchase_orders = BatchPurchaseOrder.objects.all()
        # Prepare data for each student in the batch
        students_fees = []
        for order in purchase_orders:
            batch = order.batch
            paid_fees = BatchPurchaseOrder.objects.filter(batch=batch, student=order.student, is_paid=True).aggregate(
                total_paid=Sum('amount'))['total_paid'] or 0
            total_fees = batch.fee_structure.total_amount if batch.fee_structure else 0
            outstanding_fees = total_fees - paid_fees
            students_fees.append({
                'student_name': order.student.full_name,
                'student_email': order.student.email,
                'total_fees': total_fees,
                'paid_fees': paid_fees,
                'outstanding_fees': outstanding_fees,
                'batch_name': batch.name,
            })

        # Apply pagination to the data
        page = self.paginate_queryset(students_fees)
        return self.get_paginated_response(page)


class FolderFileViewSet(viewsets.ViewSet):
    """
    A ViewSet to handle operations related to Folders and Files within a Batch.
    """
    queryset = Batch.objects.all()

    # Helper method to get the batch
    def get_batch(self, pk):
        return get_object_or_404(Batch, pk=pk)

    # 1. Create a new folder within the batch
    @action(detail=True, methods=['post'], url_path='create-folder')
    def create_folder(self, request, pk=None):
        batch = self.get_batch(pk)  # Get the batch using pk (batch_id)
        request.data['batch'] = batch.id  # Set the batch ID in the request data
        serializer = FolderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 2. Create a new file within a folder in the batch
    @action(detail=True, methods=['post'], url_path='folders/(?P<folder_id>[^/.]+)/create-file')
    def create_file(self, request, pk=None, folder_id=None):
        batch = self.get_batch(pk)  # Get the batch
        # If no folder_id is provided, use or create the Home folder
        if folder_id is None:
            folder, created = Folder.objects.get_or_create(title='Home', batch=batch)
        else:
            folder = get_object_or_404(Folder, id=folder_id)

        request.data['folder'] = folder.id  # Set folder ID in request data
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 3. Rename a folder
    @action(detail=True, methods=['patch'], url_path='folders/(?P<folder_id>[^/.]+)/rename-folder')
    def rename_folder(self, request, pk=None, folder_id=None):
        folder = get_object_or_404(Folder, id=folder_id)
        folder.title = request.data.get('title', folder.title)  # Update folder title
        folder.save()
        return Response({'status': 'Folder renamed', 'title': folder.title}, status=status.HTTP_200_OK)

    # 4. Rename a file
    @action(detail=True, methods=['patch'], url_path='files/(?P<file_id>[^/.]+)/rename-file')
    def rename_file(self, request, pk=None, file_id=None):
        file = get_object_or_404(File, id=file_id)
        file.title = request.data.get('title', file.title)  # Update file title
        file.save()
        return Response({'status': 'File renamed', 'title': file.title}, status=status.HTTP_200_OK)

    # 5. Delete a folder
    @action(detail=True, methods=['delete'], url_path='folders/(?P<folder_id>[^/.]+)/delete-folder')
    def delete_folder(self, request, pk=None, folder_id=None):
        folder = get_object_or_404(Folder, id=folder_id)
        folder.delete()  # Delete the folder
        return Response({'status': 'Folder deleted'}, status=status.HTTP_204_NO_CONTENT)

    # 6. Delete a file
    @action(detail=True, methods=['delete'], url_path='files/(?P<file_id>[^/.]+)/delete-file')
    def delete_file(self, request, pk=None, file_id=None):
        file = get_object_or_404(File, id=file_id)
        file.delete()  # Delete the file
        return Response({'status': 'File deleted'}, status=status.HTTP_204_NO_CONTENT)

    # 7. Toggle lock status of a file (lock/unlock)
    @action(detail=True, methods=['patch'], url_path='files/(?P<file_id>[^/.]+)/toggle-lock-file')
    def toggle_lock_file(self, request, pk=None, file_id=None):
        file = get_object_or_404(File, id=file_id)
        file.is_locked = not file.is_locked  # Toggle the lock status
        file.save()
        return Response({'status': 'Lock status toggled', 'is_locked': file.is_locked}, status=status.HTTP_200_OK)
