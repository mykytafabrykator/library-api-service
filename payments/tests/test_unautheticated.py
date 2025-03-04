from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from payments.tests.base import PAYMENTS_URL, payment_detail_url


class UnauthenticatedPaymentsTests(APITestCase):
    """Test payment API access for unauthenticated users"""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_user_cannot_access_payments(self):
        """Test that unauthenticated users cannot access payments"""
        result = self.client.get(PAYMENTS_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_retrieve_payment(self):
        """Test that unauthenticated users cannot retrieve a payment"""
        url = payment_detail_url(1)
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
