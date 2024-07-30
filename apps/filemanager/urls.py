from django.urls import path

from .views import (
    FileDetailView,
    FileListCreateView,
    FolderDetailView,
    FolderHierarchyView,
    FolderListCreateView,
)

urlpatterns = [
    path("api/folders/", FolderListCreateView.as_view(), name="folder-list-create"),
    path("api/folders/<int:pk>/", FolderDetailView.as_view(), name="folder-detail"),
    path("api/files/", FileListCreateView.as_view(), name="file-list-create"),
    path("api/files/<int:pk>/", FileDetailView.as_view(), name="file-detail"),
    path(
        "api/folder-hierarchy/", FolderHierarchyView.as_view(), name="folder-hierarchy"
    ),
]
