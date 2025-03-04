from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, mixins

from payments.models import Payment
from payments.serializers import (
    PaymentRetrieveSerializer,
    PaymentListSerializer
)


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Payment.objects.select_related(
            "borrowing__book",
            "borrowing__user"
        )

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(borrowing__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentRetrieveSerializer

        return PaymentListSerializer
