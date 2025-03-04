from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.tests.base import create_sample_user, TOKEN_URL


class AuthTokenTests(APITestCase):
    """Test JWT token authentication"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_sample_user(password="testpass123")

    def test_create_token(self):
        """Test obtaining JWT token"""
        payload = {"email": self.user.email, "password": "testpass123"}
        result = self.client.post(TOKEN_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertIn("access", result.data)
        self.assertIn("refresh", result.data)
