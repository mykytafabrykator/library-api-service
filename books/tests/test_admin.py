from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.tests.base import (
    BaseBookTests,
    BOOKS_URL,
    create_sample_book,
    book_detail_url
)


class AdminBookTests(BaseBookTests):
    """Test book API access for admin users"""

    def setUp(self):
        """Set up API client for an admin user."""
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@test.com",
            password="adminpass",
            first_name="Admin",
            last_name="User"
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_admin_can_create_book(self):
        """Test that admin can create a new book"""
        payload = {
            "title": "New Admin Book",
            "author": "Admin Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": 3.99,
        }
        result = self.client.post(BOOKS_URL, payload, format="json")

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)
        book = Book.objects.first()
        self.assertEqual(book.title, payload["title"])

    def test_admin_can_update_book(self):
        """Test that admin can update an existing book"""
        book = create_sample_book()
        url = book_detail_url(book.id)
        payload = {"title": "Updated Admin Book"}

        result = self.client.patch(url, payload, format="json")
        book.refresh_from_db()

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(book.title, payload["title"])

    def test_admin_can_delete_book(self):
        """Test that admin can delete an existing book"""
        book = create_sample_book()
        url = book_detail_url(book.id)

        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)
