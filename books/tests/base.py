from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from books.models import Book
from books.serializers import BookSerializer

BOOKS_URL = reverse("books:book-list")


def create_sample_book(**params) -> Book:
    """Create a sample book"""
    defaults = {
        "title": "Test Book",
        "author": "Test Author",
        "cover": "SOFT",
        "inventory": 5,
        "daily_fee": 1.51
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def book_detail_url(book_id: int) -> str:
    """Return the book detail URL"""
    return reverse("books:book-detail", args=[book_id])


class BaseBookTests(APITestCase):
    """Base test class for books API"""

    def test_list_books(self):
        """Test that book listing is accessible"""
        create_sample_book(title="Book 1")
        create_sample_book(title="Book 2")

        result = self.client.get(BOOKS_URL)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.data, serializer.data)

    def test_retrieve_book(self):
        """Test retrieving a specific book"""
        book = create_sample_book()
        url = book_detail_url(book.id)

        result = self.client.get(url)
        serializer = BookSerializer(book)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_retrieve_non_existent_book(self):
        """Test retrieving a non-existent book returns 404"""
        url = book_detail_url(999)

        result = self.client.get(url)

        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)


class UserCannotModifyBooksMixin:
    """Test mixin to ensure users cannot modify books"""

    def test_user_cannot_modify_books(self):
        """Test that users cannot create, update, or delete books"""
        book = create_sample_book()
        url = book_detail_url(book.id)

        payload = {
            "title": "Updated Title",
            "author": "Updated Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": 2.99,
        }

        methods = [
            ("post", BOOKS_URL, payload),
            ("put", url, payload),
            ("patch", url, {"title": "Patched Title"}),
            ("delete", url, None),
        ]

        expected_status = status.HTTP_401_UNAUTHORIZED
        if getattr(self, "user", None):
            expected_status = status.HTTP_403_FORBIDDEN

        for method, endpoint, data in methods:
            request_func = getattr(self.client, method)
            result = request_func(endpoint, data, format="json")

            self.assertEqual(
                result.status_code, expected_status,
                f"User should not be able to {method.upper()} {endpoint}"
            )
