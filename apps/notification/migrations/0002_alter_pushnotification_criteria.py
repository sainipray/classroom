# Generated by Django 5.0.7 on 2024-12-13 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pushnotification',
            name='criteria',
            field=models.CharField(choices=[('course', 'Course'), ('batch', 'Batch'), ('student', 'Student'), ('general', 'General')], max_length=20),
        ),
    ]