from django.db import models
from django_extensions.db.models import TimeStampedModel


class Banner(TimeStampedModel):
    title = models.CharField(max_length=255, verbose_name="Banner Title")
    image = models.CharField(max_length=255, verbose_name="Image URL")
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name="External Link")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        ordering = ["-created"]  # Order by the latest created time (from TimeStampedModel)

    def __str__(self):
        return self.title
