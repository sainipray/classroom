from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from abstract.views import CustomResponseMixin
from .models import FreeResource, Folder, File
from .serializers import FreeResourceSerializer, FileSerializer, FolderSerializer
from ..utils.functions import merge_and_sort_items


class FreeResourceViewSet(CustomResponseMixin):
    queryset = FreeResource.objects.all()
    serializer_class = FreeResourceSerializer

    def build_breadcrumb(self, folder):
        breadcrumb = []
        current_folder = folder
        while current_folder is not None:
            breadcrumb.append({'id': current_folder.id, 'title': current_folder.title})
            current_folder = current_folder.parent  # Traverse up to the parent folder

        # Reverse the breadcrumb list to have the root folder at the start
        breadcrumb.reverse()
        return breadcrumb

    @action(detail=True, methods=['get'], url_path='folder-structure')
    def get_folder_structure(self, request, pk=None):
        resource = self.get_object()
        folder_id = request.query_params.get('folder_id')  # Get folder ID from query parameters

        if folder_id:
            try:
                folder = Folder.objects.get(id=folder_id, resource=resource)
            except Folder.DoesNotExist:
                return Response({'detail': 'Folder not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Get files (files) of the current folder
            files = File.objects.filter(folder=folder).order_by('order')
            file_serializer = FileSerializer(files, many=True)

            # Get immediate subfolders
            subfolders = Folder.objects.filter(parent=folder).order_by('order')
            subfolder_serializer = FolderSerializer(subfolders, many=True)

            # Use the utility function to merge and sort
            merged_structure = merge_and_sort_items(subfolder_serializer.data, file_serializer.data)
            breadcrumb = self.build_breadcrumb(folder)

            folder_structure = {
                'id': folder.id,
                'title': folder.title,
                'items': merged_structure
            }
        else:
            # If no folder_id is provided, return the root folder structure
            root_folder, _ = Folder.objects.get_or_create(resource=resource, parent__isnull=True, title='Home')

            # Get files (files) of the current folder
            file_serializer = FileSerializer(root_folder.files.all().order_by('order'), many=True)

            # Get immediate subfolders
            subfolder_serializer = FolderSerializer(root_folder.folders.all().order_by('order'), many=True)

            # Use the utility function to merge and sort
            merged_structure = merge_and_sort_items(subfolder_serializer.data, file_serializer.data)
            breadcrumb = [{'id': root_folder.id, 'title': root_folder.title}]

            folder_structure = {
                'id': root_folder.id,
                'title': root_folder.title,
                'items': merged_structure
            }

        return Response({'resource_id': resource.id, 'folder_structure': folder_structure, 'breadcrumb': breadcrumb},
                        status=status.HTTP_200_OK)


class FolderFileViewSet(viewsets.ViewSet):
    """
    A ViewSet to handle operations related to Folders and Files within a resource.
    """
    queryset = FreeResource.objects.all()

    # Helper method to get the resource
    def get_resource(self, pk):
        return get_object_or_404(FreeResource, pk=pk)

    # 1. Create a new folder within the resource
    @action(detail=True, methods=['post'], url_path='create-folder')
    def create_folder(self, request, pk=None):
        resource = self.get_resource(pk)  # Get the resource using pk (resource_id)
        request.data['resource'] = resource.id  # Set the resource ID in the request data
        serializer = FolderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # 2. Create a new file within a folder in the resource
    @action(detail=True, methods=['post'], url_path='folders/(?P<folder_id>[^/.]+)/create-file')
    def create_file(self, request, pk=None, folder_id=None):
        resource = self.get_resource(pk)  # Get the resource
        # If no folder_id is provided, use or create the Home folder
        if folder_id is None:
            folder, created = Folder.objects.get_or_create(title='Home', resource=resource)
        else:
            folder = get_object_or_404(Folder, id=folder_id)

        request.data['folder'] = folder.id  # Set folder ID in request data
        serializer = FileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # 3. Rename a folder
    @action(detail=True, methods=['patch'], url_path='folders/(?P<folder_id>[^/.]+)/rename-folder')
    def rename_folder(self, request, pk=None, folder_id=None):
        folder = get_object_or_404(Folder, id=folder_id)
        folder.title = request.data.get('title', folder.title)  # Update folder title
        folder.save()
        return Response({'status': 'Folder renamed', 'title': folder.title}, status=status.HTTP_200_OK)

    # 4. Rename a file
    @action(detail=True, methods=['patch'], url_path='files/(?P<file_id>[^/.]+)/rename-file')
    def rename_file(self, request, pk=None, file_id=None):
        file = get_object_or_404(File, id=file_id)
        file.title = request.data.get('title', file.title)  # Update file title
        file.save()
        return Response({'status': 'File renamed', 'title': file.title}, status=status.HTTP_200_OK)

    # 5. Delete a folder
    @action(detail=True, methods=['delete'], url_path='folders/(?P<folder_id>[^/.]+)/delete-folder')
    def delete_folder(self, request, pk=None, folder_id=None):
        folder = get_object_or_404(Folder, id=folder_id)
        folder.delete()  # Delete the folder
        return Response({'status': 'Folder deleted'}, status=status.HTTP_204_NO_CONTENT)

    # 6. Delete a file
    @action(detail=True, methods=['delete'], url_path='files/(?P<file_id>[^/.]+)/delete-file')
    def delete_file(self, request, pk=None, file_id=None):
        file = get_object_or_404(File, id=file_id)
        file.delete()  # Delete the file
        return Response({'status': 'File deleted'}, status=status.HTTP_204_NO_CONTENT)



    # 7. Update order of folder or file (based on type)
    @action(detail=True, methods=['patch'], url_path='update-order')
    def update_order(self, request, pk=None):
        # Extract the 'type' (folder or file) and the 'id' and 'order'
        item_type = request.data.get('type')  # 'folder' or 'file'
        item_id = request.data.get('id')
        new_order = request.data.get('order')

        if not item_type or not item_id or new_order is None:
            return Response({'error': 'Type, id, and order are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the course
        resource = self.get_resource(pk)

        if item_type == 'folder':
            item = get_object_or_404(Folder, id=item_id, resource=resource)
        elif item_type == 'file':
            item = get_object_or_404(File, id=item_id, folder__resource=resource)
        else:
            return Response({'error': 'Invalid type. Should be "folder" or "file".'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the order
        item.order = new_order
        item.save()

        return Response({'status': f'{item_type.capitalize()} order updated', 'order': item.order}, status=status.HTTP_200_OK)
