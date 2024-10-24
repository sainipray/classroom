# Generated by Django 5.0.7 on 2024-10-16 15:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('-created',), 'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterModelOptions(
            name='coursecategorysubcategory',
            options={'ordering': ('-created',), 'verbose_name': 'Course Category and Subcategory', 'verbose_name_plural': 'Course Categories and Subcategories'},
        ),
        migrations.AlterModelOptions(
            name='coursepurchaseorder',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterModelOptions(
            name='file',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterModelOptions(
            name='folder',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterModelOptions(
            name='subcategory',
            options={'ordering': ('-created',), 'verbose_name': 'Subcategory', 'verbose_name_plural': 'Subcategories'},
        ),
    ]
