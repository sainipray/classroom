# apps/payment/models.py

from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.db.models import TimeStampedModel

User = get_user_model()


class Transaction(TimeStampedModel):
    CONTENT_CHOICES = [
        ('course', 'Course'),
        ('batch', 'Batch'),
        ('test_series', 'Test Series'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    content_type = models.CharField(max_length=20, choices=CONTENT_CHOICES)
    content_id = models.PositiveIntegerField()  # Reference to Course, Batch, or Test Series ID
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount paid
    transaction_id = models.CharField(max_length=255, unique=True)  # Razorpay Order ID
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
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

    def __str__(self):
        return f'Transaction {self.transaction_id} for {self.content_type.capitalize()} {self.content_id}'

    class Meta:
        ordering = ('-created',)
