# Generated by Django 5.1.6 on 2025-03-02 16:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("borrowings", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("PENDING", "Pending"), ("PAID", "Paid")], max_length=7
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("PAYMENT", "Payment"), ("FINE", "Fine")], max_length=7
                    ),
                ),
                ("session_url", models.URLField(blank=True, null=True)),
                ("session_id", models.CharField(max_length=255, unique=True)),
                (
                    "borrowing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payments",
                        to="borrowings.borrowing",
                    ),
                ),
            ],
        ),
    ]
