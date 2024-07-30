from django.urls import path

from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    SubcategoryDetailView,
    SubcategoryListCreateView,
)

urlpatterns = [
    path("categories/", CategoryListCreateView.as_view(), name="category_list_create"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category_detail"),
    path(
        "subcategories/",
        SubcategoryListCreateView.as_view(),
        name="subcategory_list_create",
    ),
    path(
        "subcategories/<int:pk>/",
        SubcategoryDetailView.as_view(),
        name="subcategory_detail",
    ),
]
