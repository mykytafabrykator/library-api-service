from rest_framework.test import APIClient
from books.tests.base import BaseBookTests, UserCannotModifyBooksMixin


class UnauthenticatedBookTests(BaseBookTests, UserCannotModifyBooksMixin):
    """Test book API access for unauthenticated users"""

    def setUp(self):
        self.client = APIClient()
