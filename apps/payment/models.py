# apps/payment/models.py

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Transaction(models.Model):
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
    coupon = models.ForeignKey('coupon.Coupon', on_delete=models.SET_NULL, null=True, blank=True)

    payment_id = models.CharField(max_length=255, null=True, blank=True)  # Razorpay Payment ID

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculate effective price based on original price and discounts
        if self.original_price is not None:
            self.price_after_coupon = self.original_price - self.discount_applied
            self.total_amount = self.price_after_coupon

            if self.gst_percentage is not None:
                gst_amount = (self.price_after_coupon * self.gst_percentage) / 100
                self.total_amount += gst_amount  # Adding GST to the effective price

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Transaction {self.transaction_id} for {self.content_type.capitalize()} {self.content_id}'

    class Meta:
        ordering = ('-created_at',)
