# Generated by Django 5.0.2 on 2024-03-03 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0020_remove_productprod_the_drive_motor_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productprod',
            name='img',
        ),
    ]
