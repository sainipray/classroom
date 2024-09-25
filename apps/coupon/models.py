from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from apps.course.models import Course  # Assuming you have a Course model

User = get_user_model()


class Coupon(TimeStampedModel):
    COUPON_TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    DISCOUNT_TYPE_CHOICES = [
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
    ]

    name = models.CharField(max_length=255, verbose_name="Offer Name")
    code = models.CharField(max_length=50, unique=True, verbose_name="Coupon Code")
    coupon_type = models.CharField(max_length=10, choices=COUPON_TYPE_CHOICES, default='public',
                                   verbose_name="Coupon Type")
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, verbose_name="Discount Type")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Discount Value")
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                              verbose_name="Max Discount Amount")
    start_datetime = models.DateTimeField(verbose_name="Start Date and Time")
    end_datetime = models.DateTimeField(null=True, blank=True, verbose_name="End Date and Time")
    lifetime = models.BooleanField(default=False, verbose_name="Lifetime")
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                          verbose_name="Minimum Order Value")
    max_uses = models.PositiveIntegerField(null=True, blank=True, verbose_name="Max Uses")
    usage_per_student = models.PositiveIntegerField(null=True, blank=True, verbose_name="Usage Per Student")
    is_visible = models.BooleanField(default=True, verbose_name="Visibility")
    status = models.BooleanField(default=True, verbose_name="Status")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_coupons",
                                   verbose_name="Created By")
    courses = models.ManyToManyField(Course, blank=True, related_name="coupons", verbose_name="Courses")

    # Tracking
    total_applied = models.PositiveIntegerField(default=0, verbose_name="Total Applied")

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        ordering = ['-created']  # Orders by most recently created
        indexes = [
            models.Index(fields=['code']),  # Index on coupon code
            models.Index(fields=['start_datetime', 'end_datetime']),  # Index on start and end datetime
            models.Index(fields=['status']),  # Index on status
        ]
        unique_together = ('code', 'coupon_type')  # Ensures the code is unique per coupon type

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if self.lifetime:
            self.end_datetime = None
        super().save(**kwargs)

    def apply_discount(self, original_price):
        """
        Apply the coupon discount to the original price.
        """
        if self.discount_type == 'fixed':
            return max(original_price - self.discount_value, 0)
        elif self.discount_type == 'percentage':
            discount = original_price * (self.discount_value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return max(original_price - discount, 0)
        return original_price

    def is_valid(self):
        """
        Check if the coupon is currently valid.
        """
        now = timezone.now()
        if not self.status:
            return False
        if self.max_uses and self.total_applied >= self.max_uses:
            return False
        if self.start_datetime and now < self.start_datetime:
            return False
        if not self.lifetime and self.end_datetime and now > self.end_datetime:
            return False
        return True

    def increment_usage(self):
        """
        Increment the total_applied count when a coupon is used.
        """
        self.total_applied += 1
        self.save()
