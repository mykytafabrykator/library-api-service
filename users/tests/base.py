from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model

USERS_URL = reverse("user:create")
TOKEN_URL = reverse("user:token_obtain_pair")
ME_URL = reverse("user:manage")


def create_sample_user(**params):
    """Create a sample user"""
    defaults = {
        "email": "test@example.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User",
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)
