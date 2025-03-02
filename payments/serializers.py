from rest_framework import serializers

from borrowings.serializers import BorrowingRetrieveSerializer
from payments.models import Payment


class PaymentListSerializer(serializers.ModelSerializer):
    money_to_pay = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        )


class PaymentDetailSerializer(serializers.ModelSerializer):
    borrowing = BorrowingRetrieveSerializer(read_only=True)
    money_to_pay = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        )
