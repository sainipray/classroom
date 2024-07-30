from django.conf import settings
from django.db import models
from django.utils import timezone


class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self",
        related_name="subfolders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="files/")
    folder = models.ForeignKey(Folder, related_name="files", on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(default=timezone.now)
    file_size = models.PositiveIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            self.file_type = self.file.name.split(".")[-1]
        super().save(*args, **kwargs)
