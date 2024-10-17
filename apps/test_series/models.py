from django.db import models
from django_extensions.db.models import TimeStampedModel, TitleSlugDescriptionModel, ActivatorModel


class TestSeriesCategory(TimeStampedModel, TitleSlugDescriptionModel, ActivatorModel):
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ('-created',)

    def __str__(self):
        return self.title


class TestSeries(TimeStampedModel):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(TestSeriesCategory, related_name='test_series', on_delete=models.CASCADE)
    total_questions = models.PositiveIntegerField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Highlight(models.Model):
    test_series = models.ForeignKey(TestSeries, related_name='highlights', on_delete=models.CASCADE)
    highlight_points = models.CharField(max_length=255)

    def __str__(self):
        return self.highlight_points
