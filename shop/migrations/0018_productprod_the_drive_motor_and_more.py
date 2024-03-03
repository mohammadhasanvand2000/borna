# Generated by Django 5.0.2 on 2024-02-28 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0017_alter_cartitem_product_alter_category_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productprod',
            name='The_drive_motor',
            field=models.CharField(blank=True, max_length=700, null=True, verbose_name='موتور محرک  دستگاه '),
        ),
        migrations.AddField(
            model_name='productprod',
            name='high_pressure_engine',
            field=models.CharField(blank=True, max_length=700, null=True, verbose_name='نوع موتور فشاردهنده بالا'),
        ),
        migrations.AddField(
            model_name='productprod',
            name='high_pressure_gearbox',
            field=models.CharField(blank=True, max_length=700, null=True, verbose_name='نوع گیربکس فشاردهنده بالا'),
        ),
        migrations.AddField(
            model_name='productprod',
            name='longitudinal_movement',
            field=models.CharField(blank=True, max_length=700, null=True, verbose_name='موتور اصلی حرکت طولی '),
        ),
        migrations.AddField(
            model_name='productprod',
            name='maximum_thickness',
            field=models.CharField(blank=True, max_length=700, null=True, verbose_name='حد اکثر ضخامت بال قابل نورد'),
        ),
        migrations.AddField(
            model_name='productprod',
            name='power_transmission',
            field=models.CharField(blank=True, max_length=700, null=True, verbose_name='انتقال نیرو در فشاردهنده ها'),
        ),
        migrations.AddField(
            model_name='productprod',
            name='pusher_engines',
            field=models.CharField(blank=True, max_length=700, null=True, verbose_name='موتور های فشار دهنده '),
        ),
        migrations.AddField(
            model_name='productprod',
            name='pusher_gearboxes',
            field=models.CharField(blank=True, max_length=700, null=True, verbose_name='گیربکس های فشار دهنده'),
        ),
        migrations.AddField(
            model_name='productprod',
            name='wing_dimensions',
            field=models.CharField(blank=True, max_length=700, null=True, verbose_name='ابعاد بال گیر'),
        ),
    ]