from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from abstract.views import CustomResponseMixin
from .models import Category, Subcategory, Course, Folder, File
from .serializers import CategorySerializer, SubcategorySerializer, CourseSerializer, CoursePriceUpdateSerializer, \
    ListCourseSerializer, FolderSerializer, FileSerializer
from ..utils.functions import merge_and_sort_items


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

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


class SubcategoryViewSet(ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "Course created successfully"}, status=status.HTTP_201_CREATED)

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
            root_folder, _ = Folder.objects.get_or_create(course=course, parent__isnull=True, title='Home')

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
