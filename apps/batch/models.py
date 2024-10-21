import random
import string

from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.db.models import TimeStampedModel

User = get_user_model()


def generate_batch_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


class Subject(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Subject Name")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ('-created',)

    def __str__(self):
        return self.name


class FeeStructure(TimeStampedModel):
    structure_name = models.CharField(max_length=255, verbose_name="Structure Name")
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fee Amount")
    installments = models.PositiveIntegerField(default=1, verbose_name="Number of Installments")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Amount")

    def save(self, **kwargs):
        # Automatically calculate the total amount
        self.total_amount = self.fee_amount * self.installments
        super().save(**kwargs)

    class Meta:
        verbose_name = "Fee Structure"
        verbose_name_plural = "Fee Structures"

    def __str__(self):
        return f"{self.structure_name} "


class Batch(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Batch Name")
    batch_code = models.CharField(max_length=8, default=generate_batch_code, unique=True, verbose_name="Batch Code")
    start_date = models.DateField(verbose_name="Start Date")
    subject = models.ForeignKey(Subject, related_name="batches", verbose_name="Subject", on_delete=models.CASCADE)
    live_class_link = models.URLField(blank=True, null=True, verbose_name="Live Class Link")
    created_by = models.ForeignKey(User, verbose_name="Created By", on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False, verbose_name="Is Published")
    fee_structure = models.ForeignKey(FeeStructure, null=True, blank=True, verbose_name="Fee Structure",
                                      on_delete=models.SET_NULL)
    thumbnail = models.CharField(max_length=255, verbose_name="Thumbnail", null=True, blank=True)

    class Meta:
        verbose_name = "Batch"
        verbose_name_plural = "Batches"
        ordering = ('-created',)

    def __str__(self):
        return self.name

    @property
    def total_enrolled_students(self):
        return self.enrollments.filter(is_approved=True).count()

    @property
    def enrolled_students(self):
        return [{'name': enroll.student.full_name, 'phone_number': enroll.student.phone_number.as_e164} for enroll in
                self.enrollments.filter(is_approved=True)]

    @property
    def student_join_request(self):
        return [{'id': enroll.id,
                 'name': enroll.student.full_name,
                 'phone_number': enroll.student.phone_number.as_e164} for enroll in
                self.enrollments.filter(is_approved=False)]

    def get_installment_details_for_user(self, user):
        """
        Retrieves all installment details for the specified student.

        Args:
            user (User): The student for whom to retrieve installment details.

        Returns:
            List[Dict]: A list of dictionaries containing installment details.
        """
        if not self.fee_structure:
            return []

        installments = []
        for installment_number in range(1, self.fee_structure.installments + 1):
            try:
                purchase_order = self.purchase_orders.get(student=user, installment_number=installment_number)
                installment_info = {
                    'installment_number': installment_number,
                    'amount': float(purchase_order.amount),
                    'is_paid': purchase_order.is_paid,
                    'payment_date': purchase_order.payment_date.isoformat() if purchase_order.payment_date else None,
                    'transaction_id': purchase_order.transaction.transaction_id if purchase_order.transaction else None
                }
            except BatchPurchaseOrder.DoesNotExist:
                # Installment not yet purchased
                installment_info = {
                    'installment_number': installment_number,
                    'amount': float(self.fee_structure.fee_amount),
                    'is_paid': False,
                    'payment_date': None,
                    'transaction_id': None
                }
            installments.append(installment_info)
        return installments

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
                extension = file.url.name.rsplit('.', 1)[-1].lower()

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
                    'url': file.url.url,  # URL to access the file
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


class Folder(TimeStampedModel):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='folders')
    batch = models.ForeignKey(Batch, related_name="folders", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Folder Title")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('-created',)


class File(TimeStampedModel):
    folder = models.ForeignKey(Folder, related_name="files", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Batch Title")
    url = models.FileField(upload_to='videos/', verbose_name="Batch File URL")
    is_locked = models.BooleanField(default=False, verbose_name="Is Locked")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('-created',)

    def save(self, **kwargs):
        # Automatically set the title from the document file name, if title is empty
        if not self.title and self.url:
            self.title = self.url.name.rsplit('/', 1)[-1]  # Get the file name only
        super(File, self).save(**kwargs)


class Enrollment(TimeStampedModel):
    batch = models.ForeignKey(Batch, related_name="enrollments", on_delete=models.CASCADE)
    student = models.ForeignKey(User, related_name="enrollments", on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False, verbose_name="Is Approved")
    approved_by = models.ForeignKey(User, verbose_name="Approved By", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('batch', 'student')
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"
        ordering = ('-created',)

    def __str__(self):
        return f"{self.student} in {self.batch}"


class LiveClass(TimeStampedModel):
    batch = models.ForeignKey(Batch, related_name="live_classes", on_delete=models.CASCADE, verbose_name="Batch")
    title = models.CharField(max_length=255, verbose_name="Class Title")
    host_link = models.URLField(verbose_name="Live Class host_link", null=True, blank=True)
    common_host_link = models.URLField(verbose_name="Live Class commonHostLink", null=True, blank=True)
    common_moderator_link = models.URLField(verbose_name="Live Class commonModeratorLink", null=True, blank=True)
    common_participant_link = models.URLField(verbose_name="Live Class commonParticipantLink", null=True, blank=True)
    date = models.DateTimeField(verbose_name="Class Date", null=True, blank=True)
    is_recorded = models.BooleanField(default=False, verbose_name="Is Recorded")
    class_id = models.CharField(max_length=255, verbose_name="Class ID", null=True, blank=True)
    status = models.CharField(max_length=255, verbose_name="Status", null=True, blank=True)
    recording_url = models.URLField(verbose_name="Recording URL", null=True, blank=True)
    duration = models.IntegerField(verbose_name="Duration", null=True, blank=True)
    recording_status = models.CharField(max_length=255, verbose_name="Recording Status", null=True, blank=True)

    class Meta:
        verbose_name = "Live Class"
        verbose_name_plural = "Live Classes"
        ordering = ('-created',)

    def __str__(self):
        return f"Live Class for {self.batch} on {self.date}"


class Attendance(TimeStampedModel):
    student = models.ForeignKey(User, related_name="attendances", on_delete=models.CASCADE)
    live_class = models.ForeignKey(LiveClass, related_name="attendances", on_delete=models.CASCADE)
    attended = models.BooleanField(default=False, verbose_name="Attended")
    analytics = models.JSONField(verbose_name="Analytics", null=True, blank=True)
    browser = models.JSONField(max_length=255, verbose_name="Browser", null=True, blank=True)
    ip = models.CharField(max_length=255, verbose_name="IP", null=True, blank=True)
    os = models.JSONField(max_length=255, verbose_name="OS", null=True, blank=True)
    start_time = models.DateTimeField(verbose_name="Start Time", null=True, blank=True)
    total_time = models.DurationField(verbose_name="Total Time", null=True, blank=True)
    live_class_link = models.URLField(verbose_name="Live class Joining Link ", null=True, blank=True)

    class Meta:
        unique_together = ('student', 'live_class')
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"
        ordering = ('-created',)

    def __str__(self):
        return f"{self.student} - {self.live_class} - {'Present' if self.attended else 'Absent'}"


class StudyMaterial(TimeStampedModel):
    batch = models.ForeignKey(Batch, related_name="study_materials", on_delete=models.CASCADE, verbose_name="Batch")
    title = models.CharField(max_length=255, verbose_name="Material Title")
    file = models.FileField(upload_to='study_materials/', blank=True, null=True, verbose_name="File")
    youtube_url = models.URLField(blank=True, null=True, verbose_name="YouTube URL")
    live_class_recording = models.ForeignKey(LiveClass, related_name="recordings", blank=True, null=True,
                                             on_delete=models.SET_NULL, verbose_name="Live Class Recording")

    class Meta:
        verbose_name = "Study Material"
        verbose_name_plural = "Study Material"
        ordering = ('-created',)


class BatchPurchaseOrder(TimeStampedModel):
    student = models.ForeignKey(User, related_name='batch_purchases', on_delete=models.CASCADE)
    batch = models.ForeignKey('Batch', related_name='purchase_orders', on_delete=models.CASCADE)
    transaction = models.ForeignKey('payment.Transaction', related_name='batch_purchase_orders',
                                    on_delete=models.CASCADE)
    installment_number = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Batch Purchase Order"
        verbose_name_plural = "Batch Purchase Orders"
        ordering = ('-created',)

    def __str__(self):
        return f"BatchPurchaseOrder {self.id} - {self.batch.name} - Installment {self.installment_number}"


