# Generated by Django 5.0.7 on 2024-10-17 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_series', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testseries',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='testseries',
            name='total_questions',
        ),
        migrations.AddField(
            model_name='testseries',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='testseries',
            name='effective_price',
            field=models.DecimalField(decimal_places=2, editable=False, max_digits=10, null=True, verbose_name='Effective Price'),
        ),
        migrations.AddField(
            model_name='testseries',
            name='is_digital',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='testseries',
            name='thumbnail',
            field=models.CharField(null=True, blank=True, max_length=255),
            preserve_default=False,
        ),
    ]