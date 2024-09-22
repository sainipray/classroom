from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView


class FileUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        file_obj = request.data['file']
        file_name = default_storage.save(file_obj.name, file_obj)
        file_url = default_storage.url(file_name)
        return Response({'file_url': file_url}, status=200)
