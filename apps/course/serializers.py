from rest_framework import serializers

from .models import Category, Subcategory, Course, CourseCategorySubCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "description", "status", "created", "modified"]


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = [
            "id",
            "category",
            "title",
            "description",
            "status",
            "created",
            "modified",
        ]


class CategorySubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategorySubCategory


class CourseSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(write_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'name', 'description', 'thumbnail', 'price', 'discount', 'effective_price',
            'validity_type', 'duration_value', 'duration_unit', 'expiry_date',
            'is_published', 'is_featured', 'categories'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        categories_data = validated_data.pop('categories', [])
        course = Course.objects.create(created_by=request.user, **validated_data)

        # Handle categories and subcategories
        for category_data in categories_data:
            category_data['category'] = Category.objects.get(id=category_data['category'])
            CourseCategorySubCategory.objects.create(course=course, **category_data)
        return course
