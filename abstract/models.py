from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel


class AbstractReview(TimeStampedModel):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_reviews",
        help_text="The user who submitted the review."
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        abstract = True
        ordering = ['-created']

    def __str__(self):
        return f"{self.student.full_name}: {self.title} ({self.rating})"
