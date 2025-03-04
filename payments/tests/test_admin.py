from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from books.tests.base import create_sample_book
from borrowings.tests.base import create_sample_user, create_sample_borrowing
from payments.tests.base import PAYMENTS_URL, payment_detail_url
from payments.models import Payment


class AdminPaymentsTests(APITestCase):
    """Test payment API access for admin users"""

    def setUp(self):
        self.client = APIClient()
        self.admin = create_sample_user(
            email="admin@example.com",
            is_staff=True
        )
        self.client.force_authenticate(user=self.admin)

    def test_admin_can_list_all_payments(self):
        """Test that an admin can list all payments"""
        book = create_sample_book()
        user1 = create_sample_user(email="user1@example.com")
        user2 = create_sample_user(email="user2@example.com")

        create_sample_borrowing(user=user1, book=book)
        create_sample_borrowing(user=user2, book=book)

        result = self.client.get(PAYMENTS_URL)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result.data), 2)  # Admin should see all payments

    def test_admin_can_retrieve_any_payment(self):
        """Test that an admin can retrieve any payment"""
        book = create_sample_book()
        user = create_sample_user(email="user@example.com")
        borrowing = create_sample_borrowing(user=user, book=book)

        payment = Payment.objects.get(borrowing=borrowing)
        url = payment_detail_url(payment.id)

        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
