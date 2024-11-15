from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from rest_framework.exceptions import ValidationError

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
    is_expired = models.BooleanField(default=False, verbose_name="Expired")
    status = models.BooleanField(default=True, verbose_name="Status")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_coupons",
                                   verbose_name="Created By")

    # If coupon is private then particular student can apply
    coupon_type = models.CharField(max_length=10, choices=COUPON_TYPE_CHOICES, default='public',
                                   verbose_name="Coupon Type")
    students = ArrayField(models.IntegerField(), null=True, blank=True, verbose_name="students")

    # if all course means, is_all_courses will be true if not then false
    courses = ArrayField(models.IntegerField(), null=True, blank=True, verbose_name="Courses")
    is_all_courses = models.BooleanField(default=False)

    total_applied = models.PositiveIntegerField(default=0, verbose_name="Total Applied")

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        ordering = ('-created',)  # Orders by most recently created
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

    def apply_discount(self, original_price: float, user, course):
        """
        Apply the coupon discount to the original price and return both discounted price and discount amount.

        Parameters:
        - original_price: The original price before discount.
        - user: The user applying the coupon (required).
        - course: The course for which the coupon is being applied (required).

        Returns:
        - discounted_price: The price after applying the discount.
        - discount_amount: The amount discounted.

        Raises:
        - ValueError: If the coupon is not valid for the user or course.
        - ValidationError: If the original price does not meet requirements.
        """

        # Validate if the coupon is still valid
        if self.end_datetime and timezone.now() > self.end_datetime:
            raise ValidationError("Coupon has expired.")

        if not self.status:
            raise ValidationError("Coupon is not active.")

        # Validate the user for private coupons
        if self.coupon_type == 'private':
            if user.id not in self.students:
                raise ValidationError("This coupon is not applicable to this user.")

        # Validate course eligibility
        if not self.is_all_courses:
            if course.id not in self.courses:
                raise ValidationError("This coupon is not applicable to this course.")

        # Check for minimum order value
        if original_price < self.min_order_value:
            raise ValidationError("The original price does not meet the minimum order value requirement.")

        # Calculate the discount amount
        if self.discount_type == 'fixed':
            discount_amount = self.discount_value
        elif self.discount_type == 'percentage':
            discount_amount = original_price * (self.discount_value / 100)
            if self.max_discount_amount:
                discount_amount = min(discount_amount, float(self.max_discount_amount))
        else:
            discount_amount = 0

        # Ensure the discount doesn't exceed the original price
        discounted_price = max(float(original_price) - float(discount_amount), 0)

        return discounted_price, discount_amount

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
        Ensures thread safety using atomic transactions.
        """
        with transaction.atomic():
            self.refresh_from_db()
            if self.max_uses and self.total_applied >= self.max_uses:
                raise ValueError("Coupon usage limit reached.")
            self.total_applied += 1
            self.save()
