from itertools import chain

from constance import config
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from abstract.views import CustomResponseMixin
from config.live_video import MeritHubAPI
from .filters import CourseFilter
from .models import Category, Subcategory, Course, Folder, File, CourseFaculty, CourseLiveClass, CoursePurchaseOrder, \
    CourseAttendance
from .serializers import CategorySerializer, SubcategorySerializer, CourseSerializer, CoursePriceUpdateSerializer, \
    ListCourseSerializer, FolderSerializer, FileSerializer, ListSubcategorySerializer, CreateCourseLiveClassSerializer, \
    RetrieveCourseLiveClassSerializer
from ..user.models import Roles
from ..utils.functions import merge_and_sort_items

User = get_user_model()


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()

        # Check if the category is being used by any course
        related_categories = category.course_category_subcategories.all()  # Assuming the related name is 'course_set'

        if related_categories.exists():
            # Collect the names of courses that use this category
            course_names = [category.course.name for category in related_categories]
            course_list = ', '.join(course_names)

            # Return a validation message
            message = {
                "detail": f"This category is already used in courses: {course_list}. "
                          "Please remove these courses first before deleting this category."
            }
            raise ValidationError(message)

        # If not used, proceed with the deletion
        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # Extract category data from the request
        category_data = {
            "title": request.data.get("title"),
            "description": request.data.get("description"),
        }

        # Extract subcategory data from the request
        subcategory_data = request.data.get("sub_categories", [])

        # Create the category
        category_serializer = self.get_serializer(data=category_data)
        category_serializer.is_valid(raise_exception=True)
        category = category_serializer.save()

        # Create subcategories
        for subcat in subcategory_data:
            subcategory_serializer = SubcategorySerializer(data={**subcat, "category": category.id})
            subcategory_serializer.is_valid(raise_exception=True)
            subcategory_serializer.save()

        return Response({'message': "Category Created successfully"}, status=status.HTTP_201_CREATED)


class SubcategoryViewSet(CustomResponseMixin):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    list_serializer_class = ListSubcategorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['category']

    def create(self, request, *args, **kwargs):
        category_id = request.data.get('category')
        sub_categories = request.data.get('sub_categories', [])

        for subcat in sub_categories:
            subcat['category'] = category_id
            subcategory_serializer = self.get_serializer(data=subcat)
            subcategory_serializer.is_valid(raise_exception=True)
            subcategory_serializer.save()

        # Return the created subcategories in the response
        return Response({"message": "Subcategories Created Successfully"}, status=status.HTTP_201_CREATED)


class CourseViewSet(CustomResponseMixin):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    list_serializer_class = ListCourseSerializer
    retrieve_serializer_class = ListCourseSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('name',)
    filterset_class = CourseFilter

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == Roles.INSTRUCTOR:
            course_ids = list(user.assign_courses.values_list('course_id', flat=True))
            return qs.filter(id__in=course_ids)
        elif user.role == Roles.MANAGER:
            return qs
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "Course created successfully"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='manage-faculty')
    def manage_faculty(self, request, pk=None):
        """
        Custom action to add or remove a faculty from a course.
        Expected data:
        {
            "faculty_id": <int>,   # ID of the faculty
            "action": "add" | "remove"  # Action to perform: add or remove
        }
        """
        course = self.get_object()  # Fetch the course based on `pk`
        faculty_id = request.data.get('faculty_id')
        action_type = request.data.get('action')

        if not faculty_id or action_type not in ['add', 'remove']:
            return Response({"detail": "Invalid data provided."}, status=status.HTTP_400_BAD_REQUEST)

        faculty = get_object_or_404(User, pk=faculty_id)
        message = ""
        if action_type == 'add':
            CourseFaculty.objects.get_or_create(course=course, faculty=faculty)
            message = "Faculty added successfully."
        elif action_type == 'remove':
            CourseFaculty.objects.filter(course=course, faculty=faculty).delete()
            message = "Faculty removed successfully."

        return Response({"detail": message}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='update-price')
    def update_price(self, request, pk=None):
        """
        Custom action to update the price and discount of a course.
        """
        course = self.get_object()
        serializer = CoursePriceUpdateSerializer(course, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Course price updated successfully",
                         "effective_price": serializer.instance.effective_price
                         }, status=status.HTTP_200_OK)

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
        course = self.get_object()
        folder_id = request.query_params.get('folder_id')  # Get folder ID from query parameters

        if folder_id:
            try:
                folder = Folder.objects.get(id=folder_id, course=course)
            except Folder.DoesNotExist:
                return Response({'detail': 'Folder not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Get files (files) of the current folder
            files = File.objects.filter(folder=folder).order_by('order')
            file_serializer = FileSerializer(files, many=True)

            # Get immediate subfolders
            subfolders = Folder.objects.filter(parent=folder).order_by('order')
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
            root_folder, _ = Folder.objects.get_or_create(course=course, parent__isnull=True, title='Home')

            # Get files (files) of the current folder
            file_serializer = FileSerializer(root_folder.files.all().order_by('order'), many=True)

            # Get immediate subfolders
            subfolder_serializer = FolderSerializer(root_folder.folders.all().order_by('order'), many=True)

            # Use the utility function to merge and sort
            merged_structure = merge_and_sort_items(subfolder_serializer.data, file_serializer.data)
            breadcrumb = [{'id': root_folder.id, 'title': root_folder.title}]

            folder_structure = {
                'id': root_folder.id,
                'title': root_folder.title,
                'items': merged_structure
            }

        return Response({'course_id': course.id, 'folder_structure': folder_structure, 'breadcrumb': breadcrumb},
                        status=status.HTTP_200_OK)


class FolderFileViewSet(viewsets.ViewSet):
    """
    A ViewSet to handle operations related to Folders and Files within a Course.
    """
    queryset = Course.objects.all()

    # Helper method to get the course
    def get_course(self, pk):
        return get_object_or_404(Course, pk=pk)

    # 1. Create a new folder within the course
    @action(detail=True, methods=['post'], url_path='create-folder')
    def create_folder(self, request, pk=None):
        course = self.get_course(pk)  # Get the course using pk (course_id)
        request.data['course'] = course.id  # Set the course ID in the request data
        serializer = FolderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # 2. Create a new file within a folder in the course
    @action(detail=True, methods=['post'], url_path='folders/(?P<folder_id>[^/.]+)/create-file')
    def create_file(self, request, pk=None, folder_id=None):
        course = self.get_course(pk)  # Get the course
        # If no folder_id is provided, use or create the Home folder
        if folder_id is None:
            folder, created = Folder.objects.get_or_create(title='Home', course=course)
        else:
            folder = get_object_or_404(Folder, id=folder_id)

        request.data['folder'] = folder.id  # Set folder ID in request data
        serializer = FileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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

    # 8. Update order of folder or file (based on type)
    @action(detail=True, methods=['patch'], url_path='update-order')
    def update_order(self, request, pk=None):
        """
        Reorder a folder or file within its parent directory.
        """
        item_id = request.data.get('id')
        item_type = request.data.get('type')  # 'folder' or 'file'
        direction = request.data.get('direction')  # 'up' or 'down'

        if item_type not in ['folder', 'file']:
            return Response({'error': 'Invalid type'}, status=status.HTTP_400_BAD_REQUEST)

        if direction not in ['up', 'down']:
            return Response({'error': 'Invalid direction'}, status=status.HTTP_400_BAD_REQUEST)

        model = Folder if item_type == 'folder' else File
        try:
            item = model.objects.get(id=item_id)
        except model.DoesNotExist:
            return Response({'error': f'{item_type.capitalize()} not found'}, status=status.HTTP_404_NOT_FOUND)

        # Determine parent directory
        parent = item.parent if item_type == 'folder' else item.folder

        with transaction.atomic():
            # Fetch all siblings (folders and files) in the parent directory
            folders = Folder.objects.filter(parent=parent).order_by('order')
            files = File.objects.filter(folder=parent).order_by('order')

            # Combine and sort by order
            siblings = sorted(chain(folders, files), key=lambda x: x.order)

            # Normalize order values to avoid gaps or duplicates
            for index, sibling in enumerate(siblings, start=1):
                if sibling.order != index:
                    sibling.order = index
                    sibling.save()

            # update item object after setting indexing
            item = model.objects.get(id=item_id)
            # Find adjacent item to swap with
            current_index = siblings.index(item)
            if direction == 'up' and current_index > 0:
                adjacent_item = siblings[current_index - 1]
            elif direction == 'down' and current_index < len(siblings) - 1:
                adjacent_item = siblings[current_index + 1]
            else:
                return Response(
                    {'error': f'{item_type.capitalize()} is already at the {"top" if direction == "up" else "bottom"}'},
                    status=status.HTTP_400_BAD_REQUEST)

            # Swap order values
            item.order, adjacent_item.order = adjacent_item.order, item.order
            item.save()
            adjacent_item.save()

        return Response({'message': f'{item_type.capitalize()} moved {direction} successfully'},
                        status=status.HTTP_200_OK)
class CreateCourseLiveClassView(APIView):

    def post(self, request):
        serializer = CreateCourseLiveClassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated data
        validated_data = serializer.validated_data
        course = validated_data['course']

        # Assuming you have configured your client ID and secret key in settings
        client_id = config.MERITHUB_CLIENT_ID
        secret_key = config.MERITHUB_CLIENT_SECRET
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
            data = api.schedule_class(
                user_id=self.request.user.id,
                class_data=class_data,
            )
            live_class = CourseLiveClass.objects.create(
                course=course,
                title=class_data['title'],
                class_id=data['classId'],
                date=class_data['startTime'],
                host_link=api.generate_url(data['hostLink']),
                common_host_link=api.generate_url(data['commonLinks']['commonHostLink']),
                common_moderator_link=api.generate_url(data['commonLinks']['commonModeratorLink']),
                common_participant_link=api.generate_url(data['commonLinks']['commonParticipantLink'])
            )
            enrolled_students = CoursePurchaseOrder.objects.filter(course=course, is_paid=True)
            students = []
            for order in enrolled_students:
                user = order.student
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
                    CourseAttendance.objects.create(student=user, live_class=live_class,
                                                    live_class_link=live_class_link)
                except User.DoesNotExist:
                    print(f"User {student['userId']}")

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Serialize the created class (assuming you have a serializer for this)
        retrieve_serializer = RetrieveCourseLiveClassSerializer(instance=live_class)
        return Response(retrieve_serializer.data, status=status.HTTP_201_CREATED)


class CourseLiveClassViewSet(mixins.DestroyModelMixin,
                             GenericViewSet):
    queryset = CourseLiveClass.objects.all()
    serializer_class = RetrieveCourseLiveClassSerializer
