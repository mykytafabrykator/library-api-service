from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from borrowings.models import Borrowing


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        PAID = "PAID", _("Paid")

    class TypeChoices(models.TextChoices):
        PAYMENT = "PAYMENT", _("Payment")
        FINE = "FINE", _("Fine")

    status = models.CharField(max_length=7, choices=StatusChoices.choices)
    type = models.CharField(max_length=7, choices=TypeChoices.choices)
    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    session_url = models.URLField(blank=True, null=True)
    session_id = models.CharField(max_length=255, unique=True)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

    @staticmethod
    def calculate_money_to_pay(borrowing) -> Decimal:
        """
        Calculate the total amount to be paid for the borrowing.
        """
        return_date = (borrowing.actual_return_date
                       or borrowing.expected_return_date)
        borrowing_days = max(1, (return_date - borrowing.borrow_date).days)

        return borrowing_days * borrowing.book.daily_fee

    def __str__(self):
        return f"{self.type} - {self.status} (${self.money_to_pay})"
