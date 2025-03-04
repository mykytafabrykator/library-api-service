from rest_framework.reverse import reverse


PAYMENTS_URL = reverse("payments:payments-list")


def payment_detail_url(payment_id: int) -> str:
    """Return the payment detail URL"""
    return reverse("payments:payments-detail", args=[payment_id])
