from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Category, Subcategory, Course, CourseCategorySubCategory, Folder, File, CourseFaculty, \
    CourseValidityPeriod

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "description", "status", "created", "modified"]

    # def validate(self, data):
    #     # Check if we are performing a delete operation
    #     request = self.context.get('request')
    #     if request and request.method == 'DELETE':
    #         # Get the category instance
    #         category = self.instance
    #         if Course.objects.filter(category=category).exists():
    #             raise serializers.ValidationError(
    #                 "Cannot delete this category as it is associated with one or more courses.")
    #     return data


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


class ListSubcategorySerializer(SubcategorySerializer):
    category = CategorySerializer(read_only=True)


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


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', ]


class CourseFacultySerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(read_only=True)

    class Meta:
        model = CourseFaculty
        fields = ['id', 'faculty', 'course']


class CourseValidityPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseValidityPeriod
        fields = ['id', 'duration_value', 'duration_unit', 'price', 'discount', 'effective_price', 'is_promoted']
        read_only_fields = ['effective_price']

    def validate(self, data):
        price = data.get('price')
        discount = data.get('discount', 0)

        if price < 0:
            raise serializers.ValidationError("Price must be a positive value.")
        if discount < 0:
            raise serializers.ValidationError("Discount must be greater than or equal to 0.")

        return data


    def update(self, instance, validated_data):
        instance.price = validated_data.get('price', instance.price)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.effective_price = instance.price - (instance.price * (instance.discount / 100))
        instance.duration_value = validated_data.get('duration_value', instance.duration_value)
        instance.duration_unit = validated_data.get('duration_unit', instance.duration_unit)
        instance.save()
        return instance


class CoursePriceUpdateSerializer(serializers.ModelSerializer):
    validity_periods = CourseValidityPeriodSerializer(many=True, required=False)

    class Meta:
        model = Course
        fields = ['price', 'discount', 'effective_price', 'expiry_date', 'duration_value', 'duration_unit',
                  'validity_type', 'validity_periods']

    def validate(self, data):
        validity_type = data.get('validity_type')
        if validity_type == 'multiple' and 'validity_periods' not in data:
            raise serializers.ValidationError("Validity periods are required for multiple validity type.")
        return data

    def update(self, instance, validated_data):
        new_validity_type = validated_data.get('validity_type', instance.validity_type)

        # Clear existing validity periods if switching away from "multiple"
        if instance.validity_type == 'multiple' and new_validity_type != 'multiple':
            CourseValidityPeriod.objects.filter(course=instance).delete()

        instance.validity_type = new_validity_type

        if new_validity_type == 'multiple':
            # Handle "Multiple Validity" type
            CourseValidityPeriod.objects.filter(course=instance).delete()
            validity_periods_data = validated_data.pop('validity_periods', [])
            for period_data in validity_periods_data:
                CourseValidityPeriod.objects.create(course=instance, **period_data)
        else:
            # Handle "Single", "Lifetime", or "Expiry Date" validity types
            instance.price = validated_data.get('price', instance.price)
            instance.discount = validated_data.get('discount', instance.discount)
            instance.effective_price = instance.price - (
                        instance.price * (instance.discount / 100)) if instance.price else instance.price
            instance.duration_value = validated_data.get('duration_value', instance.duration_value)
            instance.duration_unit = validated_data.get('duration_unit', instance.duration_unit)
            instance.expiry_date = validated_data.get('expiry_date', instance.expiry_date)

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


class ListCourseSerializer(serializers.ModelSerializer):
    categories_subcategories = CategorySubCategorySerializer(many=True)
    created_by = serializers.ReadOnlyField(source='created_by.full_name')
    faculties = CourseFacultySerializer(source='course_faculties', many=True, read_only=True)
    validity_periods = CourseValidityPeriodSerializer(many=True, read_only=True)
    total_enrolled_students = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = '__all__'
