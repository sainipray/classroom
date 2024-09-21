from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Category, Subcategory, Course
from .serializers import CategorySerializer, SubcategorySerializer, CourseSerializer


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
    filter_backends = (DjangoFilterBackend, )
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

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
