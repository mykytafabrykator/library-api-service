from django.db import transaction
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingRetrieveSerializer,
    BorrowingCreateSerializer
)


class BorrowingsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Borrowing.objects.select_related("book", "user")
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset

        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if is_active is not None:
            queryset = queryset.filter(
                actual_return_date__isnull=is_active.lower() == "true"
            )

        if self.request.user.is_staff:
            if user_id:
                return queryset.filter(user_id=user_id)

            return queryset

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingRetrieveSerializer
        if self.action == "borrow_book":
            return BorrowingCreateSerializer

        return BorrowingListSerializer

    @action(detail=False, methods=["POST"], url_path="borrow")
    def borrow_book(self, request):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            with transaction.atomic():
                book = serializer.validated_data["book"]
                book.inventory -= 1
                book.save(update_fields=["inventory"])

                serializer.save(user=request.user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
