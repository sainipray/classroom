# Generated by Django 5.0.7 on 2024-11-11 06:40

import django.db.models.deletion
import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('free_resource', '0002_freeresource_link_alter_freeresource_resource_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='freeresource',
            name='document_file',
        ),
        migrations.RemoveField(
            model_name='freeresource',
            name='link',
        ),
        migrations.RemoveField(
            model_name='freeresource',
            name='resource_type',
        ),
        migrations.RemoveField(
            model_name='freeresource',
            name='video_file',
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('title', models.CharField(max_length=255, verbose_name='Folder Title')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='folders', to='free_resource.folder')),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='folders', to='free_resource.freeresource')),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('title', models.CharField(max_length=255, verbose_name='Lecture Title')),
                ('url', models.FileField(upload_to='videos/', verbose_name='Lecture Video')),
                ('is_locked', models.BooleanField(default=False, verbose_name='Is Locked')),
                ('folder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='free_resource.folder')),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
    ]