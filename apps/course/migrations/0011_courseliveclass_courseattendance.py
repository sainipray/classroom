# Generated by Django 5.0.7 on 2024-12-03 05:25

import django.db.models.deletion
import django_extensions.db.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0010_alter_course_thumbnail'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseLiveClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('title', models.CharField(max_length=255, verbose_name='Class Title')),
                ('host_link', models.URLField(blank=True, null=True, verbose_name='Live Class host_link')),
                ('common_host_link', models.URLField(blank=True, null=True, verbose_name='Live Class commonHostLink')),
                ('common_moderator_link', models.URLField(blank=True, null=True, verbose_name='Live Class commonModeratorLink')),
                ('common_participant_link', models.URLField(blank=True, null=True, verbose_name='Live Class commonParticipantLink')),
                ('date', models.DateTimeField(blank=True, null=True, verbose_name='Class Date')),
                ('is_recorded', models.BooleanField(default=False, verbose_name='Is Recorded')),
                ('class_id', models.CharField(blank=True, max_length=255, null=True, verbose_name='Class ID')),
                ('status', models.CharField(blank=True, max_length=255, null=True, verbose_name='Status')),
                ('recording_url', models.URLField(blank=True, null=True, verbose_name='Recording URL')),
                ('duration', models.IntegerField(blank=True, null=True, verbose_name='Duration')),
                ('recording_status', models.CharField(blank=True, max_length=255, null=True, verbose_name='Recording Status')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='live_classes', to='course.course', verbose_name='Course')),
            ],
            options={
                'verbose_name': 'Live Class',
                'verbose_name_plural': 'Live Classes',
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='CourseAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('attended', models.BooleanField(default=False, verbose_name='Attended')),
                ('analytics', models.JSONField(blank=True, null=True, verbose_name='Analytics')),
                ('browser', models.JSONField(blank=True, max_length=255, null=True, verbose_name='Browser')),
                ('ip', models.CharField(blank=True, max_length=255, null=True, verbose_name='IP')),
                ('os', models.JSONField(blank=True, max_length=255, null=True, verbose_name='OS')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='Start Time')),
                ('total_time', models.IntegerField(blank=True, null=True, verbose_name='Total Time')),
                ('live_class_link', models.URLField(blank=True, null=True, verbose_name='Live class Joining Link ')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_attendances', to=settings.AUTH_USER_MODEL)),
                ('live_class', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='course_attendance', to='course.courseliveclass')),
            ],
            options={
                'verbose_name': 'Course Attendance',
                'verbose_name_plural': 'Course Attendances',
                'ordering': ('-created',),
            },
        ),
    ]