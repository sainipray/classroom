from rest_framework import serializers

from .models import Category, Subcategory, Course


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
    categories = CategorySerializer(many=True, required=False)
    thumbnail = serializers.ImageField(required=False)

    class Meta:
        model = Course

class CourseSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, required=False)
    thumbnail = serializers.ImageField(required=False)

    class Meta:
        model = Course
        fields = [
            'id', 'name', 'description', 'thumbnail', 'price', 'discount', 'effective_price',
            'validity_type', 'duration_value', 'duration_unit', 'expiry_date',
            'is_published', 'is_featured', 'categories'
        ]

    def create(self, validated_data):
        categories_data = validated_data.pop('categories', [])
        course = Course.objects.create(**validated_data)

        # Handle categories and subcategories
        for category_data in categories_data:
            subcategories_data = category_data.pop('subcategories', [])
            category, created = Category.objects.get_or_create(
                name=category_data['name'], defaults=category_data)
            for subcategory_data in subcategories_data:
                Subcategory.objects.get_or_create(
                    name=subcategory_data['name'], category=category, defaults=subcategory_data)
            course.categories.add(category)

        return course
