from rest_framework import serializers

from .models import Category, Subcategory, Course, CourseCategorySubCategory, Folder, File


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
    category = CategorySerializer(read_only=True)

    class Meta:
        model = CourseCategorySubCategory
        fields = '__all__'


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


class ListCourseSerializer(serializers.ModelSerializer):
    categories_subcategories = CategorySubCategorySerializer(many=True)
    created_by = serializers.ReadOnlyField(source='created_by.full_name')

    class Meta:
        model = Course
        fields = '__all__'


class CoursePriceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['price', 'discount', 'effective_price', 'expiry_date', 'duration_value', 'duration_unit',
                  'validity_type']

    def validate(self, data):
        price = data.get('price', None)
        discount = data.get('discount', None)
        validity_type = data.get('validity_type', None)
        duration_value = data.get('duration_value', None)
        expiry_date = data.get('expiry_date', None)

        if price is not None and discount is not None:
            if discount < 0:
                raise serializers.ValidationError("Discount must be greater than or equal to 0")
            if price < 0:
                raise serializers.ValidationError("Price must be a positive value.")

        # Additional validation based on validity type
        if validity_type == 'single':
            if duration_value is None:
                raise serializers.ValidationError("Duration value is required for single validity.")
        elif validity_type == 'expiry_date':
            if expiry_date is None:
                raise serializers.ValidationError("Expiry date is required for expiry date validity.")

        return data

    def update(self, instance, validated_data):
        price = validated_data.get('price', instance.price)
        discount = validated_data.get('discount', instance.discount)
        validity_type = validated_data.get('validity_type', instance.validity_type)
        duration_value = validated_data.get('duration_value', instance.duration_value)
        duration_unit = validated_data.get('duration_unit', instance.duration_unit)
        expiry_date = validated_data.get('expiry_date', instance.expiry_date)

        # Recalculate effective price based on price and discount
        if price is not None and discount is not None:
            effective_price = discount
        else:
            effective_price = price

        # Update instance with the validated data
        instance.price = price
        instance.discount = discount
        instance.effective_price = effective_price
        instance.validity_type = validity_type
        instance.duration_value = duration_value
        instance.duration_unit = duration_unit
        instance.expiry_date = expiry_date

        instance.save()
        return instance


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['id', 'course', 'title', 'parent', 'created']


class FileSerializer(serializers.ModelSerializer):
    title = serializers.CharField(read_only=True)

    class Meta:
        model = File
        fields = ['id', 'title', 'folder', 'url', 'created', 'is_locked']


