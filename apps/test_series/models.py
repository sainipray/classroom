from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_extensions.db.models import TimeStampedModel, TitleSlugDescriptionModel, ActivatorModel

User = get_user_model()


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
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    effective_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Effective Price",
                                          editable=False, null=True)
    description = models.TextField(blank=True, null=True)
    thumbnail = models.CharField(max_length=255, null=True, blank=True)
    is_digital = models.BooleanField(default=True)
    url = models.CharField(max_length=255)
    highlights = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    is_published = models.BooleanField(default=False, verbose_name="Is Published")
    created_by = models.ForeignKey(User, verbose_name="Created By", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.price and self.discount:
            self.effective_price = self.price - (self.price * (self.discount / 100))
        else:
            self.effective_price = self.price
        super().save(**kwargs)


# class TestSeriesStudentAddress(TimeStampedModel):
#     street = models.CharField(max_length=255)
#     city = models.CharField(max_length=100)
#     state = models.CharField(max_length=100)
#     postal_code = models.CharField(max_length=20)
#     country = models.CharField(max_length=100)
#
#     def __str__(self):
#         return f"{self.street}, {self.city}, {self.state}, {self.country} - {self.postal_code}"

class TestSeriesPurchaseOrder(TimeStampedModel):
    student = models.ForeignKey(User, related_name='test_series_purchases', on_delete=models.CASCADE)
    test_series = models.ForeignKey(TestSeries, related_name='purchase_orders', on_delete=models.CASCADE)
    transaction = models.ForeignKey('payment.Transaction', related_name='test_series_purchase_orders',
                                    on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Test Series Purchase Order"
        verbose_name_plural = "Test Series Purchase Orders"
        ordering = ('-created',)

    def __str__(self):
        return f"TestSeriesPurchaseOrder {self.id} - {self.test_series.name}"
