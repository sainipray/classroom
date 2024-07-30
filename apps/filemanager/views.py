from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import File, Folder
from .serializers import FileSerializer, FolderSerializer


class FolderListCreateView(generics.ListCreateAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class FolderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]


class FileListCreateView(generics.ListCreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]


class FolderHierarchyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        def get_subfolders(folder):
            subfolders = folder.subfolders.all()
            return {
                "id": folder.id,
                "name": folder.name,
                "subfolders": [get_subfolders(subfolder) for subfolder in subfolders],
                "files": list(folder.files.values("id", "name")),
            }

        root_folders = Folder.objects.filter(parent=None)
        hierarchy = [get_subfolders(folder) for folder in root_folders]
        return Response(hierarchy)
