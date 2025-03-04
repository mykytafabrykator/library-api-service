from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingCreateSerializer


BORROWINGS_URL = reverse("borrowings:borrowings-list")


def borrowing_detail_url(borrowing_id: int) -> str:
    """Return the borrowing detail URL"""
    return reverse("borrowings:borrowings-detail", args=[borrowing_id])


def borrow_book_url(book_id: int) -> str:
    """Return the URL for borrowing a book"""
    return reverse("books:book-borrow-book", args=[book_id])


def create_sample_user(**params):
    """Create a sample user"""
    defaults = {
        "email": "test@email.com",
        "password": "strongpassword",
        "first_name": "test",
        "last_name": "test",
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def create_sample_borrowing(user, book, **params) -> Borrowing:
    """Create a sample borrowing using serializer to ensure payment creation"""
    payload = {
        "borrow_date": "2025-01-01",
        "expected_return_date": "2025-01-10"
    }
    payload.update(params)

    serializer = BorrowingCreateSerializer(
        data=payload,
        context={"book": book}
    )
    serializer.is_valid(raise_exception=True)
    return serializer.save(user=user, book=book)
