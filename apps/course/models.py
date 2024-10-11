from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_extensions.db.models import TimeStampedModel, TitleSlugDescriptionModel, ActivatorModel

from apps.coupon.models import Coupon
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
    name = models.CharField(max_length=255, verbose_name="Course Name")
    description = models.TextField(verbose_name="Course Description")
    thumbnail = models.CharField(max_length=255, verbose_name="Thumbnail")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price", null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Discount")
    effective_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Effective Price",
                                          editable=False, null=True)
    validity_type = models.CharField(max_length=20, choices=VALIDITY_CHOICES, default='single',
                                     verbose_name="Validity Type")

    # Single and Multiple Validity
    duration_value = models.PositiveIntegerField(null=True, blank=True, verbose_name="Duration Value")
    duration_unit = models.CharField(max_length=10, choices=DURATION_UNITS, default='days',
                                     verbose_name="Duration Unit")

    expiry_date = models.DateTimeField(null=True, blank=True, verbose_name="Expiry Date")
    is_published = models.BooleanField(default=False, verbose_name="Is Published")
    is_featured = models.BooleanField(default=False, verbose_name="Is Featured")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Author")

    def save(self, *args, **kwargs):
        if self.price and self.discount:
            self.effective_price = self.price - (self.price * (self.discount / 100))
        else:
            self.effective_price = self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def content(self):
        # Define the file extensions for videos and images
        VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
        IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

        # Initialize counts
        counts = {
            'videos': 0,
            'images': 0
        }

        def fetch_folder_structure(folder):
            nonlocal counts  # Allows access to the counts dictionary defined in the outer scope

            folder_data = {
                'id': folder.id,
                'title': folder.title,
                'files': [],
                'subfolders': []
            }
            # Fetch files within the folder
            for file in folder.files.all():
                # Determine the file extension
                extension = file.document.name.rsplit('.', 1)[-1].lower()

                # Increment counts based on file type
                if extension in VIDEO_EXTENSIONS:
                    counts['videos'] += 1
                elif extension in IMAGE_EXTENSIONS:
                    counts['images'] += 1

                # TODO we don't need to show urls of each file that is locked or if student not purchased course
                # Append file data
                folder_data['files'].append({
                    'id': file.id,
                    'title': file.title,
                    'document': file.document.url,  # URL to access the file
                    'is_locked': file.is_locked
                })

            # Recursively fetch subfolders
            for subfolder in folder.folders.all():
                folder_data['subfolders'].append(fetch_folder_structure(subfolder))

            return folder_data

        folder_structure = []
        # Start from top-level folders (where parent is None)
        for folder in self.folders.filter(parent__isnull=True):
            folder_structure.append(fetch_folder_structure(folder))

        # Prepare the final data with directory structure and counts
        data = {
            'directory': folder_structure,
            'videos': counts['videos'],
            'images': counts['images']
        }

        return data
    @property
    def categories_info(self):
        categories_data = []
        for category_subcategory in self.categories_subcategories.all():
            categories_data.append({
                'category': str(category_subcategory.category),
                'subcategories': category_subcategory.subcategories
            })
        return categories_data


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


class CourseCategorySubCategory(TimeStampedModel):
    course = models.ForeignKey(Course, related_name="categories_subcategories", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name="course_category_subcategories", on_delete=models.CASCADE)
    subcategories = ArrayField(models.CharField(max_length=255), blank=True, default=list, verbose_name="Subcategories")

    class Meta:
        unique_together = ('course', 'category')
        verbose_name = "Course Category and Subcategory"
        verbose_name_plural = "Course Categories and Subcategories"

    def __str__(self):
        return f"{self.course} - {self.category} - {', '.join(self.subcategories)}"


class Folder(TimeStampedModel):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='folders')
    course = models.ForeignKey(Course, related_name="folders", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Folder Title")

    def __str__(self):
        return self.title


class File(TimeStampedModel):
    folder = models.ForeignKey(Folder, related_name="files", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Lecture Title")
    document = models.FileField(upload_to='videos/', verbose_name="Lecture Video")
    is_locked = models.BooleanField(default=False, verbose_name="Is Locked")

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        # Automatically set the title from the document file name, if title is empty
        if not self.title and self.document:
            self.title = self.document.name.rsplit('/', 1)[-1]  # Get the file name only
        super(File, self).save(**kwargs)


class Assignment(TimeStampedModel):
    course = models.ForeignKey(
        'Course',  # Assuming Course model is in the same app or imported
        related_name="assignments",
        on_delete=models.CASCADE,
        verbose_name="Course"
    )
    title = models.CharField(max_length=255, verbose_name="Assignment Title")
    description = models.TextField(blank=True, verbose_name="Assignment Description")
    due_date = models.DateTimeField(verbose_name="Due Date")
    max_marks = models.PositiveIntegerField(verbose_name="Maximum Marks")
    is_published = models.BooleanField(default=True, verbose_name="Is Published")

    class Meta:
        ordering = ['due_date']
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"

    def __str__(self):
        return self.title


class AssignmentSubmission(TimeStampedModel):
    assignment = models.ForeignKey(
        Assignment,
        related_name="submissions",
        on_delete=models.CASCADE,
        verbose_name="Assignment"
    )
    student = models.ForeignKey(
        Student,
        related_name="assignment_submissions",
        on_delete=models.CASCADE,
        verbose_name="Student"
    )
    submission_date = models.DateTimeField(auto_now_add=True, verbose_name="Submission Date")
    file = models.FileField(upload_to='assignments/submissions/', verbose_name="Submission File")
    is_graded = models.BooleanField(default=False, verbose_name="Is Graded")

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['submission_date']
        verbose_name = "Assignment Submission"
        verbose_name_plural = "Assignment Submissions"

    def __str__(self):
        return f"{self.assignment.title} - {self.student.user.full_name}"


class AssignmentFeedback(TimeStampedModel):
    submission = models.OneToOneField(
        AssignmentSubmission,
        related_name="feedback",
        on_delete=models.CASCADE,
        verbose_name="Submission"
    )
    instructor = models.ForeignKey(
        User,
        related_name="assignment_feedbacks",
        on_delete=models.CASCADE,
        verbose_name="Instructor"
    )
    feedback = models.TextField(blank=True, verbose_name="Feedback")
    grade = models.PositiveIntegerField(verbose_name="Grade")

    class Meta:
        verbose_name = "Assignment Feedback"
        verbose_name_plural = "Assignment Feedbacks"

    def __str__(self):
        return f"Feedback for {self.submission.assignment.title} - {self.submission.student.full_name}"


class CoursePurchaseOrder(TimeStampedModel):
    student = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Student")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Course")
    transaction = models.ForeignKey('payment.Transaction', on_delete=models.CASCADE)

    def __str__(self):
        return f"Order for {self.course.name} by {self.student.full_name} on {self.created}"

    class Meta:
        ordering = ['-created']
