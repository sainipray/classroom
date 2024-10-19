from django.db import models
from django_extensions.db.models import TimeStampedModel


class FreeResource(TimeStampedModel):
    class ResourceType(models.TextChoices):
        VIDEO = 'video', 'Video'
        DOCUMENT = 'document', 'Document'

    title = models.CharField(max_length=255)
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices
    )
    link = models.URLField(null=True, blank=True)
    thumbnail = models.CharField(max_length=255, blank=True, null=True)
    video_file = models.CharField(max_length=255, null=True, blank=True)
    document_file = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title
