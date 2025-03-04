from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from books.tests.base import create_sample_book
from borrowings.tests.base import (
    BORROWINGS_URL,
    borrowing_detail_url,
    create_sample_user,
    create_sample_borrowing,
)
from django.contrib.auth import get_user_model


class AdminBorrowingTests(APITestCase):
    """Test borrowing API access for admin users"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="adminpass",
            first_name="Admin",
            last_name="User",
        )
        self.client.force_authenticate(user=self.admin_user)

        self.user = create_sample_user(email="user@example.com")
        self.book = create_sample_book()
        self.borrowing = create_sample_borrowing(
            user=self.user,
            book=self.book
        )

    def test_admin_can_view_all_borrowings(self):
        """Test that an admin can see all borrowings"""
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_admin_can_retrieve_any_borrowing(self):
        """Test that an admin can retrieve any borrowing"""
        url = borrowing_detail_url(self.borrowing.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
