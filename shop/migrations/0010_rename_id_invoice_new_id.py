# Generated by Django 4.1.1 on 2022-11-11 18:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0009_alter_invoice_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="invoice",
            old_name="id",
            new_name="new_id",
        ),
    ]