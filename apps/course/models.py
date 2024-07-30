from django.db import models
from django_extensions.db.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Category Name")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


class Subcategory(TimeStampedModel):
    category = models.ForeignKey(
        Category,
        related_name="subcategories",
        on_delete=models.CASCADE,
        verbose_name="Category",
    )
    name = models.CharField(max_length=255, verbose_name="Subcategory Name")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name
