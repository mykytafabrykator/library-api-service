from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.tests.base import USERS_URL, ME_URL


class UnauthenticatedUserTests(APITestCase):
    """Test unauthenticated user actions"""

    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        """Test that an unauthenticated user can register"""
        payload = {
            "email": "newuser@example.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "User",
        }
        result = self.client.post(USERS_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

    def test_cannot_access_me(self):
        """Test that unauthenticated users cannot access their profile"""
        result = self.client.get(ME_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
