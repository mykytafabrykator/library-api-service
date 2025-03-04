from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="borrowings",
    )

    @staticmethod
    def validate_borrowing(
            borrow_date,
            expected_return_date,
            actual_return_date=None
    ):
        """Validate borrowing dates to ensure logical consistency."""
        if expected_return_date < borrow_date:
            raise ValidationError(
                "Expected return date cannot be earlier than borrow date."
            )

        if actual_return_date and actual_return_date < borrow_date:
            raise ValidationError(
                "Actual return date cannot be earlier than borrow date."
            )

    def clean(self):
        """Run borrowing validation before saving."""
        Borrowing.validate_borrowing(
            self.borrow_date,
            self.expected_return_date,
            self.actual_return_date
        )

    def __str__(self):
        return (f"{self.user.email} borrowed {self.book.title} "
                f"on {self.borrow_date}")
