from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from books.tests.base import create_sample_book
from borrowings.models import Borrowing
from borrowings.tests.base import (
    BORROWINGS_URL,
    borrowing_detail_url,
    create_sample_user,
    create_sample_borrowing, borrow_book_url,
)
from payments.models import Payment


class AuthenticatedBorrowingTests(APITestCase):
    """Test borrowing API access for authenticated users"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_sample_user(
            email="user@example.com",
            password="testpass",
            first_name="user",
            last_name="test",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_borrowings(self):
        """Test that an authenticated user can
        list only their own borrowings"""
        book = create_sample_book()
        create_sample_borrowing(user=self.user, book=book)

        another_user = create_sample_user()
        create_sample_borrowing(user=another_user, book=book)

        result = self.client.get(BORROWINGS_URL)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        # Only own borrowings should be listed
        self.assertEqual(len(result.data), 1)

    def test_retrieve_borrowing(self):
        """Test retrieving a specific borrowing"""
        book = create_sample_book()
        borrowing = create_sample_borrowing(user=self.user, book=book)

        url = borrowing_detail_url(borrowing.id)
        result = self.client.get(url)

        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_borrowing_creates_payment(self):
        """Test that creating a borrowing also creates a Stripe payment"""
        book = create_sample_book(inventory=1)

        payload = {
            "borrow_date": "2025-03-01",
            "expected_return_date": "2025-03-05"
        }

        result = self.client.post(borrow_book_url(book.id), payload)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

        borrowing = Borrowing.objects.get(id=result.data["id"])
        payments = Payment.objects.filter(borrowing=borrowing)

        self.assertEqual(payments.count(), 1)
        payment = payments.first()

        self.assertEqual(payment.status, Payment.StatusChoices.PENDING)
        self.assertEqual(payment.type, Payment.TypeChoices.PAYMENT)
        self.assertIsNotNone(payment.session_url)
        self.assertIsNotNone(payment.session_id)

        book.refresh_from_db()
        self.assertEqual(book.inventory, 0)

    def test_return_borrowing(self):
        """Test returning a borrowed book"""
        book = create_sample_book()
        borrowing = create_sample_borrowing(user=self.user, book=book)
        self.assertEqual(book.inventory, 4)

        url = reverse("borrowings:borrowings-return-book", args=[borrowing.id])
        result = self.client.post(url)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        borrowing.refresh_from_db()
        book.refresh_from_db()

        self.assertIsNotNone(borrowing.actual_return_date)
        self.assertEqual(book.inventory, 5)

    def test_create_borrowing_fails_when_book_unavailable(self):
        """Test that borrowing creation fails when book is out of stock"""
        book = create_sample_book(inventory=0)

        payload = {
            "borrow_date": "2025-03-01",
            "expected_return_date": "2025-03-05"
        }

        result = self.client.post(borrow_book_url(book.id), payload)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("book", result.data)

    def test_cannot_return_already_returned_borrowing(self):
        """Test that a borrowing cannot be returned twice"""
        book = create_sample_book()
        borrowing = create_sample_borrowing(user=self.user, book=book)

        url = reverse("borrowings:borrowings-return-book", args=[borrowing.id])
        self.client.post(url)
        result = self.client.post(url)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
