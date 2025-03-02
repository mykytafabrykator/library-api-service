# Generated by Django 5.1.6 on 2025-03-02 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="money_to_pay",
            field=models.DecimalField(decimal_places=2, default=10.51, max_digits=10),
            preserve_default=False,
        ),
    ]
