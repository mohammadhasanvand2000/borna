# Generated by Django 4.1.1 on 2022-11-17 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0013_remove_invoice_ref_id_payment"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="date_modified",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
