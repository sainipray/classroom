from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from abstract.views import CustomResponseMixin
from .models import Category, Subcategory, Course, Folder, File
from .serializers import CategorySerializer, SubcategorySerializer, CourseSerializer, CoursePriceUpdateSerializer, \
    ListCourseSerializer, FolderSerializer, FileSerializer
from .utils import merge_and_sort_items


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

    @action(detail=True, methods=['post'], url_path='create-folder')
    def create_folder(self, request, pk=None):
        course = self.get_object()
        request.data['course'] = course.id  # Set the course ID
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
            home_folder, created = Folder.objects.get_or_create(title='Home', course=self.get_object())
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
