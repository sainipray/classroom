# Generated by Django 5.0.7 on 2024-10-16 15:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0003_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coupon',
            options={'ordering': ('-created',), 'verbose_name': 'Coupon', 'verbose_name_plural': 'Coupons'},
        ),
    ]
