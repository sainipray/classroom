from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.db.models import TimeStampedModel

from apps.batch.models import Batch
from apps.course.models import Course

User = get_user_model()


class Announcement(TimeStampedModel):
    title = models.CharField(max_length=255)
    message = models.TextField()

    # Announcement types
    is_global = models.BooleanField(default=False)  # Global announcement

    # Batch/Course-specific announcements
    batch = models.ForeignKey(Batch, null=True, blank=True, related_name="announcements", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, null=True, blank=True, related_name="announcements", on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"
        ordering = ('-created',)

    def save(self, *args, **kwargs):
        if not self.batch and (not self.course):
            self.is_global = True
        super().save(*args, **kwargs)
