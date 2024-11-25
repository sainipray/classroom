# apps/payment/models.py
from constance import config
from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.db.models import TimeStampedModel

from apps.batch.models import Batch
from apps.course.models import Course
from apps.test_series.models import TestSeries

User = get_user_model()


class Transaction(TimeStampedModel):
    class ContentType(models.TextChoices):
        COURSE = 'course', 'Course'
        BATCH = 'batch', 'Batch'
        TEST_SERIES = 'test_series', 'Test Series'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    class PaymentType(models.TextChoices):
        RAZORPAY = 'razorpay', 'Razorpay'
        MANUAL = 'manual', 'Manual'

    payment_type = models.CharField(max_length=20, choices=PaymentType.choices, default=PaymentType.RAZORPAY)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    content_type = models.CharField(max_length=20, choices=ContentType.choices)
    content_id = models.PositiveIntegerField()  # Reference to Course, Batch, or Test Series ID
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount paid
    transaction_id = models.CharField(max_length=255, unique=True)  # Razorpay Order ID
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )

    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_after_coupon = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                             blank=True)  # Price after coupon
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                       blank=True)  # Total amount after applying GST
    platform_fees = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                        blank=True)
    internet_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                           blank=True)
    coupon = models.ForeignKey('coupon.Coupon', on_delete=models.SET_NULL, null=True, blank=True)

    payment_id = models.CharField(max_length=255, null=True, blank=True)  # Razorpay Payment ID
    invoice_counter = models.PositiveIntegerField(default=1, null=True, blank=True)

    def __str__(self):
        return f'Transaction {self.transaction_id} for {self.content_type.capitalize()} {self.content_id}'

    class Meta:
        ordering = ('-created',)

    def save(self, *args, **kwargs):
        # Save the instance first in case it's being saved with a status update
        super().save(*args, **kwargs)

        # Only proceed if the payment status is COMPLETED and no invoice_counter is set
        if self.payment_status == self.PaymentStatus.COMPLETED and not self.invoice_counter:
            current_value = config.INVOICE_NUMBER_COUNTER
            if not current_value:
                current_value = 1
            self.invoice_counter = current_value
            setattr(config, 'INVOICE_NUMBER_COUNTER', int(current_value) + 1)
            super().save(*args, **kwargs)

    @property
    def gst_calculation(self):
        return self.total_amount - self.total_price_before_gst

    @property
    def after_discount_price(self):
        return self.original_price - self.discount_applied

    @property
    def total_price_before_gst(self):
        return self.original_price + self.platform_fees + self.internet_charges

    @property
    def student_name(self):
        return self.user.full_name if self.user else "Unknown"

    @property
    def content_name(self):
        if self.content_type == self.ContentType.COURSE:
            return Course.objects.filter(id=self.content_id).first().name if Course.objects.filter(
                id=self.content_id).exists() else "Unknown Course"
        elif self.content_type == self.ContentType.BATCH:
            return Batch.objects.filter(id=self.content_id).first().name if Batch.objects.filter(
                id=self.content_id).exists() else "Unknown Batch"
        elif self.content_type == self.ContentType.TEST_SERIES:
            return TestSeries.objects.filter(id=self.content_id).first().name if Batch.objects.filter(
                id=self.content_id).exists() else "Unknown Batch"
        return "Unknown Content"
