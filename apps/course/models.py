from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.db.models import TimeStampedModel, TitleSlugDescriptionModel, ActivatorModel

from apps.user.models import Student

User = get_user_model()


class Category(TimeStampedModel, TitleSlugDescriptionModel, ActivatorModel):
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title


class Subcategory(TimeStampedModel, TitleSlugDescriptionModel, ActivatorModel):
    category = models.ForeignKey(
        Category,
        related_name="subcategories",
        on_delete=models.CASCADE,
        verbose_name="Category",
    )

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"

    def __str__(self):
        return self.title


class Course(TimeStampedModel):
    VALIDITY_CHOICES = [
        ('single', 'Single Validity'),
        ('multiple', 'Multiple Validity'),
        ('lifetime', 'Lifetime Validity'),
        ('expiry_date', 'Expiry Date'),
    ]

    DURATION_UNITS = [
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years'),
    ]
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Author")
    name = models.CharField(max_length=255, verbose_name="Course Name")
    description = models.TextField(verbose_name="Course Description")
    thumbnail = models.ImageField(upload_to='course_thumbnails/', verbose_name="Thumbnail")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price", null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Discount")
    effective_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Effective Price",
                                          editable=False)
    validity_type = models.CharField(max_length=20, choices=VALIDITY_CHOICES, default='single',
                                     verbose_name="Validity Type")

    # Single and Multiple Validity
    duration_value = models.PositiveIntegerField(null=True, blank=True, verbose_name="Duration Value")
    duration_unit = models.CharField(max_length=10, choices=DURATION_UNITS, default='days',
                                     verbose_name="Duration Unit")

    expiry_date = models.DateTimeField(null=True, blank=True, verbose_name="Expiry Date")
    is_published = models.BooleanField(default=False, verbose_name="Is Published")
    is_featured = models.BooleanField(default=False, verbose_name="Is Featured")

    def save(self, *args, **kwargs):
        if self.price and self.discount:
            self.effective_price = self.price - (self.price * (self.discount / 100))
        else:
            self.effective_price = self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AdvancedCourseSettings(TimeStampedModel):
    TAX_CHOICES = [
        (0, '0%'),
        (5, '5%'),
        (18, '18%'),
        (25, '25%'),
    ]

    course = models.OneToOneField(Course, related_name="advanced_settings", on_delete=models.CASCADE)
    internet_handling_charges = models.BooleanField(default=False, verbose_name="Internet Handling Charges")
    tax_details = models.IntegerField(choices=TAX_CHOICES, default=0, verbose_name="Tax Details")
    course_sharing = models.BooleanField(default=False, verbose_name="Course Sharing")
    offline_material = models.BooleanField(default=False, verbose_name="Course Has Offline Material For Shipment")
    offline_download_videos = models.BooleanField(default=False, verbose_name="Offline Download Of Videos")
    pdf_download_app = models.BooleanField(default=False, verbose_name="PDF Download Permissions in APP")
    pdf_access_web = models.BooleanField(default=False, verbose_name="PDF permissions on Web")
    live_classes = models.BooleanField(default=False, verbose_name="LIVE Classes")
    add_restrictions_videos = models.BooleanField(default=False, verbose_name="Add Restrictions To Videos")
    update_existing_videos = models.BooleanField(default=False, verbose_name="Update Existing Videos")

    def __str__(self):
        return f"Advanced settings for {self.course.name}"

#
# class CourseCategorySubCategory(TimeStampedModel):
#     course = models.ForeignKey(Course, related_name="categories_subcategories", on_delete=models.CASCADE)
#     category = models.ForeignKey(Category, related_name="course_category_subcategories", on_delete=models.CASCADE)
#     subcategories = ArrayField(models.CharField(max_length=255), blank=True, default=list, verbose_name="Subcategories")
#
#     class Meta:
#         unique_together = ('course', 'category')
#         verbose_name = "Course Category and Subcategory"
#         verbose_name_plural = "Course Categories and Subcategories"
#
#     def __str__(self):
#         return f"{self.course} - {self.category} - {', '.join(self.subcategories)}"
#
#
# class Section(TimeStampedModel):
#     course = models.ForeignKey(Course, related_name="sections", on_delete=models.CASCADE)
#     title = models.CharField(max_length=255, verbose_name="Section Title")
#     description = models.TextField(blank=True, null=True, verbose_name="Section Description")
#
#     def __str__(self):
#         return self.title
#
#
# class Content(TimeStampedModel):
#     section = models.ForeignKey(Section, related_name="contents", on_delete=models.CASCADE)
#     title = models.CharField(max_length=255, verbose_name="Lecture Title")
#     description = models.TextField(blank=True, null=True, verbose_name="Lecture Description")
#     video = models.FileField(upload_to='lecture_videos/', verbose_name="Lecture Video")
#     document = models.FileField(upload_to='videos/', verbose_name="Lecture Video")
#     is_locked = models.BooleanField(default=False, verbose_name="Is Locked")
#
#     def __str__(self):
#         return self.title
#
#
# class Assignment(TimeStampedModel):
#     course = models.ForeignKey(
#         'Course',  # Assuming Course model is in the same app or imported
#         related_name="assignments",
#         on_delete=models.CASCADE,
#         verbose_name="Course"
#     )
#     title = models.CharField(max_length=255, verbose_name="Assignment Title")
#     description = models.TextField(blank=True, verbose_name="Assignment Description")
#     due_date = models.DateTimeField(verbose_name="Due Date")
#     max_marks = models.PositiveIntegerField(verbose_name="Maximum Marks")
#     is_published = models.BooleanField(default=True, verbose_name="Is Published")
#
#     class Meta:
#         ordering = ['due_date']
#         verbose_name = "Assignment"
#         verbose_name_plural = "Assignments"
#
#     def __str__(self):
#         return self.title
#
#
# class AssignmentSubmission(TimeStampedModel):
#     assignment = models.ForeignKey(
#         Assignment,
#         related_name="submissions",
#         on_delete=models.CASCADE,
#         verbose_name="Assignment"
#     )
#     student = models.ForeignKey(
#         Student,
#         related_name="assignment_submissions",
#         on_delete=models.CASCADE,
#         verbose_name="Student"
#     )
#     submission_date = models.DateTimeField(auto_now_add=True, verbose_name="Submission Date")
#     file = models.FileField(upload_to='assignments/submissions/', verbose_name="Submission File")
#     is_graded = models.BooleanField(default=False, verbose_name="Is Graded")
#
#     class Meta:
#         unique_together = ('assignment', 'student')
#         ordering = ['submission_date']
#         verbose_name = "Assignment Submission"
#         verbose_name_plural = "Assignment Submissions"
#
#     def __str__(self):
#         return f"{self.assignment.title} - {self.student.user.full_name}"
#
#
# class AssignmentFeedback(TimeStampedModel):
#     submission = models.OneToOneField(
#         AssignmentSubmission,
#         related_name="feedback",
#         on_delete=models.CASCADE,
#         verbose_name="Submission"
#     )
#     instructor = models.ForeignKey(
#         User,
#         related_name="assignment_feedbacks",
#         on_delete=models.CASCADE,
#         verbose_name="Instructor"
#     )
#     feedback = models.TextField(blank=True, verbose_name="Feedback")
#     grade = models.PositiveIntegerField(verbose_name="Grade")
#
#     class Meta:
#         verbose_name = "Assignment Feedback"
#         verbose_name_plural = "Assignment Feedbacks"
#
#     def __str__(self):
#         return f"Feedback for {self.submission.assignment.title} - {self.submission.student.full_name}"
