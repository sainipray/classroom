# Generated by Django 5.0.7 on 2024-12-06 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0011_courseliveclass_courseattendance'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='file',
            options={'ordering': ('order', '-created')},
        ),
        migrations.AlterModelOptions(
            name='folder',
            options={'ordering': ('order', '-created')},
        ),
        migrations.AddField(
            model_name='file',
            name='order',
            field=models.PositiveIntegerField(default=0, verbose_name='Order'),
        ),
        migrations.AddField(
            model_name='folder',
            name='order',
            field=models.PositiveIntegerField(default=0, verbose_name='Order'),
        ),
    ]
