# Generated by Django 5.0.7 on 2024-10-16 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0003_alter_category_options_alter_course_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='file',
            old_name='document',
            new_name='url',
        ),
    ]
