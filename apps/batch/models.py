import random
import string

from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.db.fields import AutoSlugField
from django_extensions.db.models import TimeStampedModel

from apps.user.models import Student
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def generate_batch_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


class Subject(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Subject Name")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def __str__(self):
        return self.name


class Batch(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Batch Name")
    batch_code = models.CharField(max_length=8, default=generate_batch_code, unique=True, verbose_name="Batch Code")
    start_date = models.DateField(verbose_name="Start Date")
    subject = models.ForeignKey(Subject, related_name="batches", verbose_name="Subject", on_delete=models.CASCADE)
    live_class_link = models.URLField(blank=True, null=True, verbose_name="Live Class Link")
    created_by = models.ForeignKey(User, verbose_name="Created By", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Batch"
        verbose_name_plural = "Batches"
        get_latest_by = 'modified'

    def __str__(self):
        return self.name

    @property
    def total_enrolled_students(self):
        return self.enrollments.count()


class Enrollment(TimeStampedModel):
    batch = models.ForeignKey(Batch, related_name="enrollments", on_delete=models.CASCADE)
    student = models.ForeignKey(User, related_name="enrollments", on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False, verbose_name="Is Approved")
    approved_by = models.ForeignKey(User, verbose_name="Approved By", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('batch', 'student')
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

    def __str__(self):
        return f"{self.student} in {self.batch}"



class LiveClass(TimeStampedModel):
    batch = models.ForeignKey(Batch, related_name="live_classes", on_delete=models.CASCADE, verbose_name="Batch")
    title = models.CharField(max_length=255, verbose_name="Class Title")
    link = models.URLField(verbose_name="Live Class Link")
    date = models.DateTimeField(verbose_name="Class Date")
    is_recorded = models.BooleanField(default=False, verbose_name="Is Recorded")

    class Meta:
        verbose_name = "Live Class"
        verbose_name_plural = "Live Classes"

    def __str__(self):
        return f"Live Class for {self.batch} on {self.date}"


class Attendance(TimeStampedModel):
    student = models.ForeignKey(Student, related_name="attendances", on_delete=models.CASCADE)
    live_class = models.ForeignKey(LiveClass, related_name="attendances", on_delete=models.CASCADE)
    attended = models.BooleanField(default=False, verbose_name="Attended")

    class Meta:
        unique_together = ('student', 'live_class')
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"

    def __str__(self):
        return f"{self.student} - {self.live_class} - {'Present' if self.attended else 'Absent'}"


class StudyMaterial(TimeStampedModel):
    batch = models.ForeignKey(Batch, related_name="study_materials", on_delete=models.CASCADE, verbose_name="Batch")
    title = models.CharField(max_length=255, verbose_name="Material Title")
    file = models.FileField(upload_to='study_materials/', blank=True, null=True, verbose_name="File")
    youtube_url = models.URLField(blank=True, null=True, verbose_name="YouTube URL")
    live_class_recording = models.ForeignKey(LiveClass, related_name="recordings", blank=True, null=True,
                                             on_delete=models.SET_NULL, verbose_name="Live Class Recording")
