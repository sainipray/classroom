from rest_framework import generics, permissions

from .models import Category, Subcategory
from .serializers import CategorySerializer, SubcategorySerializer


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class SubcategoryListCreateView(generics.ListCreateAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class SubcategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    permission_classes = [permissions.IsAuthenticated]
