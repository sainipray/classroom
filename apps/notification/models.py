from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.batch.models import Batch
from apps.course.models import Course

User = get_user_model()


class PushNotification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField(null=True, blank=True)
    criteria = models.CharField(max_length=20, choices=[("course", "Course"), ("batch", "Batch"), ("student", "Student"),
                                                        ("general", "General")])
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, null=True, blank=True, on_delete=models.CASCADE)
    student_ids = ArrayField(models.IntegerField(), blank=True,
                             default=list)  # Store student IDs as an array of integers
    sent_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Notification: {self.title} ({self.sent_at})"
