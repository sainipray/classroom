# Generated by Django 5.0.7 on 2024-09-22 08:08

import django.contrib.postgres.fields
import django.db.models.deletion
import django_extensions.db.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_alter_course_price'),
        ('user', '0004_alter_student_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('title', models.CharField(max_length=255, verbose_name='Assignment Title')),
                ('description', models.TextField(blank=True, verbose_name='Assignment Description')),
                ('due_date', models.DateTimeField(verbose_name='Due Date')),
                ('max_marks', models.PositiveIntegerField(verbose_name='Maximum Marks')),
                ('is_published', models.BooleanField(default=True, verbose_name='Is Published')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='course.course', verbose_name='Course')),
            ],
            options={
                'verbose_name': 'Assignment',
                'verbose_name_plural': 'Assignments',
                'ordering': ['due_date'],
            },
        ),
        migrations.CreateModel(
            name='AssignmentSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('submission_date', models.DateTimeField(auto_now_add=True, verbose_name='Submission Date')),
                ('file', models.FileField(upload_to='assignments/submissions/', verbose_name='Submission File')),
                ('is_graded', models.BooleanField(default=False, verbose_name='Is Graded')),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='course.assignment', verbose_name='Assignment')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignment_submissions', to='user.student', verbose_name='Student')),
            ],
            options={
                'verbose_name': 'Assignment Submission',
                'verbose_name_plural': 'Assignment Submissions',
                'ordering': ['submission_date'],
                'unique_together': {('assignment', 'student')},
            },
        ),
        migrations.CreateModel(
            name='AssignmentFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('feedback', models.TextField(blank=True, verbose_name='Feedback')),
                ('grade', models.PositiveIntegerField(verbose_name='Grade')),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignment_feedbacks', to=settings.AUTH_USER_MODEL, verbose_name='Instructor')),
                ('submission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='feedback', to='course.assignmentsubmission', verbose_name='Submission')),
            ],
            options={
                'verbose_name': 'Assignment Feedback',
                'verbose_name_plural': 'Assignment Feedbacks',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('title', models.CharField(max_length=255, verbose_name='Section Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Section Description')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='course.course')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('title', models.CharField(max_length=255, verbose_name='Lecture Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Lecture Description')),
                ('video', models.FileField(upload_to='lecture_videos/', verbose_name='Lecture Video')),
                ('document', models.FileField(upload_to='videos/', verbose_name='Lecture Video')),
                ('is_locked', models.BooleanField(default=False, verbose_name='Is Locked')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='course.section')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CourseCategorySubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('subcategories', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, default=list, size=None, verbose_name='Subcategories')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_category_subcategories', to='course.category')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories_subcategories', to='course.course')),
            ],
            options={
                'verbose_name': 'Course Category and Subcategory',
                'verbose_name_plural': 'Course Categories and Subcategories',
                'unique_together': {('course', 'category')},
            },
        ),
    ]