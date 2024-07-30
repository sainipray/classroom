from rest_framework import serializers

from .models import Category, Subcategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "is_active", "created", "modified"]


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = [
            "id",
            "category",
            "name",
            "description",
            "is_active",
            "created",
            "modified",
        ]
