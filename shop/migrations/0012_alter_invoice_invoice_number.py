# Generated by Django 4.1.1 on 2022-11-11 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0011_rename_new_id_invoice_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="invoice_number",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
