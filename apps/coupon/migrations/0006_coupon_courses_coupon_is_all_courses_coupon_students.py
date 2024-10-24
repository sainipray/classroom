# Generated by Django 5.0.7 on 2024-10-22 08:18

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0005_remove_coupon_courses'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='courses',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None, verbose_name='Courses'),
        ),
        migrations.AddField(
            model_name='coupon',
            name='is_all_courses',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='coupon',
            name='students',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None, verbose_name='students'),
        ),
    ]
