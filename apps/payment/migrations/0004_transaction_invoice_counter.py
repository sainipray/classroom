# Generated by Django 5.0.7 on 2024-11-26 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_transaction_payment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='invoice_counter',
            field=models.PositiveIntegerField(blank=True, default=1, null=True),
        ),
    ]
