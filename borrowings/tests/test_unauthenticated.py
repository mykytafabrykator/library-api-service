from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from borrowings.tests.base import BORROWINGS_URL, borrowing_detail_url


class UnauthenticatedBorrowingTests(APITestCase):
    """Test borrowing API access for unauthenticated users"""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_user_cannot_access_borrowings(self):
        """Test that unauthenticated users cannot access the borrowings API"""
        endpoints = [
            ("get", BORROWINGS_URL),
            ("post", BORROWINGS_URL, {}),
            ("get", borrowing_detail_url(1)),
            ("delete", borrowing_detail_url(1)),
        ]

        for method, url, *data in endpoints:
            request_func = getattr(self.client, method)
            response = request_func(url, *data, format="json")

            self.assertEqual(
                response.status_code, status.HTTP_401_UNAUTHORIZED,
                "Unauthenticated user should not be "
                f"able to {method.upper()} {url}"
            )
