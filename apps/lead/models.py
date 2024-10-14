from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.db.models import TimeStampedModel

User = get_user_model()


class Lead(TimeStampedModel):
    SOURCE_CHOICES = [
        ('Justdial', 'Justdial'),
        ('Sulekha', 'Sulekha'),
        ('Hoardings', 'Hoardings'),
        ('Online Marketing', 'Online Marketing'),
        ('Reference', 'Reference'),
        ('Others', 'Others'),
    ]

    STATUS_CHOICES = [
        ('High Interest', 'High Interest'),
        ('Medium Interest', 'Medium Interest'),
        ('Low Interest', 'Low Interest'),
        ('Converted', 'Converted'),
        ('Lost', 'Lost'),
    ]

    student_name = models.CharField(max_length=255, verbose_name="Student Name")
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number")
    enquiry_date = models.DateField(verbose_name="Enquiry Date")
    assign_lead = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Assign Lead")
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, verbose_name="Source")
    enquiry_status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name="Enquiry Status")
    class_and_subject = models.CharField(max_length=255, verbose_name="Class and Subject", blank=True, null=True)
    followup_type = models.CharField(max_length=255, verbose_name="Followup Type")
    followup_date = models.DateField(verbose_name="Followup Date")
    followup_time = models.TimeField(verbose_name="Followup Time")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        ordering = ('-created',)

    def __str__(self):
        return f"{self.student_name} - {self.enquiry_status}"
