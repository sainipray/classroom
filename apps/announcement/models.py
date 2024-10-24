from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth.models import User

from apps.batch.models import Batch
from apps.course.models import Course


class Announcement(TimeStampedModel):
    title = models.CharField(max_length=255)
    message = models.TextField()

    # Announcement types
    is_global = models.BooleanField(default=False)  # Global announcement

    # Batch/Course-specific announcements
    batch = models.ForeignKey(Batch, null=True, blank=True, related_name="announcements", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, null=True, blank=True, related_name="announcements", on_delete=models.CASCADE)


    def __str__(self):
        return self.title


class AnnouncementSeenStatus(models.Model):
    student = models.ForeignKey(User, related_name='announcement_status', on_delete=models.CASCADE)
    announcement = models.ForeignKey(Announcement, related_name='seen_statuses', on_delete=models.CASCADE)
    seen = models.BooleanField(default=False)
    seen_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.student.username} - {self.announcement.title} (Seen: {self.seen})'
