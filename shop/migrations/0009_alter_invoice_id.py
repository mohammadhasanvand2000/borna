# Generated by Django 4.1.1 on 2022-11-11 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0008_invoice_cartitem"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]