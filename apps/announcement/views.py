from rest_framework import viewsets

from abstract.views import CustomResponseMixin
from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementViewSet(CustomResponseMixin):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    def get_queryset(self):
        # Add any filtering based on user or permissions if needed
        queryset = super().get_queryset()

        # Example filter: Only return global announcements or those for specific batches/courses
        batch_id = self.request.query_params.get('batch')
        course_id = self.request.query_params.get('course')
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
        elif course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset
