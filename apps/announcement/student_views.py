from datetime import timedelta

from django.utils import timezone

from abstract.views import CustomResponseMixin
from .models import Announcement
from .student_serializers import StudentAnnouncementSerializer
from ..batch.models import Batch
from ..course.models import Course


class StudentAnnouncementViewSet(CustomResponseMixin):
    queryset = Announcement.objects.all()
    serializer_class = StudentAnnouncementSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # return queryset
        user = self.request.user

        # Calculate the date 5 days ago from today
        five_days_ago = timezone.now() - timedelta(days=5)

        # Start by including all global announcements created in the last 5 days
        announcements = queryset.filter(is_global=True, created__gte=five_days_ago)

        # Include batch-specific announcements if the student is enrolled and created in the last 5 days
        batch_announcements = queryset.filter(
            batch__in=[batch for batch in Batch.objects.all() if batch.is_student_enrolled(user)],
            created__gte=five_days_ago
        )
        announcements = announcements | batch_announcements

        # Include course-specific announcements if the student is enrolled and created in the last 5 days
        course_announcements = queryset.filter(
            course__in=[course for course in Course.objects.all() if course.is_student_enrolled(user)],
            created__gte=five_days_ago
        )
        announcements = announcements | course_announcements

        # Apply specific filtering based on request parameters
        course_id = self.request.query_params.get('course')
        batch_id = self.request.query_params.get('batch')

        if course_id:
            announcements = announcements.filter(course_id=course_id)
        elif batch_id:
            announcements = announcements.filter(batch_id=batch_id)

        return announcements.distinct()
