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

    @property
    def money_to_pay(self) -> Decimal:
        """Calculate the total cost of borrowing."""
        borrowing = self.borrowing

        return_date = (borrowing.actual_return_date
                       or borrowing.expected_return_date)
        borrowing_days = max(1, (return_date - borrowing.borrow_date).days)

        return borrowing_days * borrowing.book.daily_fee

    def __str__(self):
        return f"{self.type} - {self.status} (${self.money_to_pay})"
