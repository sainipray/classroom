from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField


class CustomUserManager(BaseUserManager):
    def create_user(
            self, email, phone_number, full_name, password=None, **extra_fields
    ):
        if not email:
            raise ValueError(_("The Email field must be set"))
        if not phone_number:
            raise ValueError(_("The Phone number field must be set"))
        if not full_name:
            raise ValueError(_("The Full name field must be set"))
        email = self.normalize_email(email)
        user = self.model(
            email=email, phone_number=phone_number, full_name=full_name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self, email, phone_number, full_name, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(
            email, phone_number, full_name, password, **extra_fields
        )


class Roles(models.TextChoices):
    STUDENT = "STUDENT", "Student"
    TEACHER = "TEACHER", "Teacher"
    ADMIN = "ADMIN", "Admin"
    INSTRUCTOR = "INSTRUCTOR", "Instructor"


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email Address")
    phone_number = PhoneNumberField(
        unique=True, region="IN", verbose_name="Phone Number"
    )
    full_name = models.CharField(max_length=100, verbose_name="Full Name")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_staff = models.BooleanField(default=False, verbose_name="Is Staff")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date Joined")
    role = models.CharField(
        max_length=50, choices=Roles.choices, default=Roles.STUDENT, verbose_name="Role"
    )

    merit_user_id = models.CharField(max_length=255, null=True, blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number", "full_name", "role"]

    def __str__(self):
        return self.phone_number.as_e164


class Student(TimeStampedModel):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="student",
        verbose_name="User",
    )
    about = models.TextField(blank=True, verbose_name="About")
    profile_photo = models.ImageField(
        upload_to="profile_photos/", blank=True, verbose_name="Profile Photo"
    )

    # Parent Information
    mother_name = models.CharField(
        max_length=100, blank=True, verbose_name="Mother's Name"
    )
    father_name = models.CharField(
        max_length=100, blank=True, verbose_name="Father's Name"
    )
    occupation = models.CharField(max_length=100, blank=True, verbose_name="Occupation")
    parent_mobile_number = PhoneNumberField(
        blank=True, null=True, region="IN", verbose_name="Parent Mobile Number"
    )
    parent_email = models.EmailField(blank=True, verbose_name="Parent Email")
    parent_profile_photo = models.ImageField(
        upload_to="parent_photos/",
        blank=True,
        verbose_name="Parent Profile Photo",
    )

    # Personal Details
    date_of_birth = models.DateField(
        blank=True, null=True, verbose_name="Date of Birth"
    )
    gender = models.CharField(max_length=10, blank=True, verbose_name="Gender")
    nationality = models.CharField(
        max_length=50, blank=True, verbose_name="Nationality"
    )
    blood_group = models.CharField(max_length=3, blank=True, verbose_name="Blood Group")

    # Address
    permanent_address = models.TextField(blank=True, verbose_name="Permanent Address")
    permanent_address_pincode = models.CharField(
        max_length=10, blank=True, verbose_name="Permanent Address Pincode"
    )
    correspondence_address = models.TextField(
        blank=True, verbose_name="Correspondence Address"
    )
    correspondence_address_pincode = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Correspondence Address Pincode",
    )

    # Educational Details
    school_name = models.CharField(
        max_length=100, blank=True, verbose_name="School Name"
    )
    college_name = models.CharField(
        max_length=100, blank=True, verbose_name="College Name"
    )
    marks_x = models.FloatField(blank=True, null=True, verbose_name="Marks in X (%)")
    x_result = models.FileField(
        upload_to="results/x/", blank=True, verbose_name="X Result"
    )
    marks_xii = models.FloatField(blank=True, null=True, verbose_name="Marks in XII (%)")
    xii_result = models.FileField(
        upload_to="results/xii/", blank=True, verbose_name="XII Result"
    )
    marks_college = models.FloatField(blank=True, null=True, verbose_name="Marks in College (%)")
    college_result = models.FileField(
        upload_to="results/college/",
        blank=True,
        verbose_name="College Result",
    )

    def __str__(self):
        return self.user.full_name


class Instructor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='instructor', null=True, blank=True)


class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher')


class DeviceSession(models.Model):
    MOBILE = 'mobile'
    DESKTOP = 'desktop'

    DEVICE_CHOICES = [
        (MOBILE, 'Mobile'),
        (DESKTOP, 'Desktop'),
    ]

    user = models.ForeignKey(CustomUser, related_name='device_sessions', on_delete=models.CASCADE)
    device_type = models.CharField(max_length=10, choices=DEVICE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)  # Auto-update with each login

    class Meta:
        unique_together = ('user', 'device_type')
        verbose_name = 'Device Session'
        verbose_name_plural = 'Device Sessions'

    def __str__(self):
        return f"{self.user} - {self.device_type}"

    """
    device_type = request.data.get('device_type')
    # Delete existing sessions for the device type
    DeviceSession.objects.filter(user=user, device_type=device_type).delete()
    # Save new device session and update last_login
    DeviceSession.objects.create(user=user, device_type=device_type, last_login=timezone.now())
    """
