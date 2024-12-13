# Generated by Django 5.0.7 on 2024-11-28 04:53

import django.db.models.deletion
import django_extensions.db.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_series', '0008_physicalproduct'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='testseries',
            name='gst',
            field=models.PositiveSmallIntegerField(default=18),
        ),
        migrations.CreateModel(
            name='PhysicalProductOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('delivery_status', models.CharField(choices=[('shipped', 'Shipped'), ('in-transit', 'In-Transit'), ('delivered', 'Delivered'), ('delivery-pending', 'Delivery Pending')], default='delivery-pending', max_length=20)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('test_series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='physical_product', to='test_series.testseries')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='physical_product_orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='PhysicalProduct',
        ),
    ]
