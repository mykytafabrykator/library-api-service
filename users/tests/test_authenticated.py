from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.tests.base import create_sample_user, ME_URL


class AuthenticatedUserTests(APITestCase):
    """Test authenticated user actions"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_sample_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_profile(self):
        """Test retrieving profile for logged-in user"""
        result = self.client.get(ME_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data["email"], self.user.email)

    def test_update_profile(self):
        """Test updating profile"""
        payload = {"first_name": "Updated", "last_name": "User"}
        self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertEqual(self.user.last_name, payload["last_name"])
