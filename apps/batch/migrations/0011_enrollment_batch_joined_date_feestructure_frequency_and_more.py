# Generated by Django 5.0.7 on 2024-10-23 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batch', '0010_alter_liveclass_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='batch_joined_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='feestructure',
            name='frequency',
            field=models.CharField(choices=[('weekly', 'Weekly'), ('monthly', 'Monthly')], max_length=10, null=True, verbose_name='Installment Frequency'),
        ),
        migrations.AddField(
            model_name='feestructure',
            name='number_of_values',
            field=models.PositiveIntegerField(default=1, null=True, verbose_name='Number of Values'),
        ),
    ]