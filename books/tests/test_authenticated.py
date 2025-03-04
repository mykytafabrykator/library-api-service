from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from books.tests.base import BaseBookTests, UserCannotModifyBooksMixin


class AuthenticatedBookTests(BaseBookTests, UserCannotModifyBooksMixin):
    """Test book API access for authenticated users"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
            first_name="Test",
            last_name="Data"
        )
        self.client.force_authenticate(user=self.user)
