from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from books.tests.base import create_sample_book
from borrowings.tests.base import create_sample_user, create_sample_borrowing
from payments.tests.base import PAYMENTS_URL, payment_detail_url
from payments.models import Payment


class AuthenticatedPaymentsTests(APITestCase):
    """Test payment API access for authenticated users"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_sample_user(email="user@example.com")
        self.client.force_authenticate(user=self.user)

    def test_list_payments(self):
        """Test that a user can only list their own payments"""
        book = create_sample_book()
        create_sample_borrowing(user=self.user, book=book)

        another_user = create_sample_user(email="another@example.com")
        create_sample_borrowing(user=another_user, book=book)

        result = self.client.get(PAYMENTS_URL)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result.data), 1)  # Only their own payments

    def test_retrieve_payment(self):
        """Test that a user can retrieve their own payment"""
        book = create_sample_book()
        borrowing = create_sample_borrowing(user=self.user, book=book)

        payment = Payment.objects.get(borrowing=borrowing)
        url = payment_detail_url(payment.id)

        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_user_cannot_access_others_payments(self):
        """Test that a user cannot retrieve another user's payment"""
        book = create_sample_book()
        another_user = create_sample_user(email="another@example.com")
        borrowing = create_sample_borrowing(user=another_user, book=book)

        payment = Payment.objects.get(borrowing=borrowing)
        url = payment_detail_url(payment.id)

        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
