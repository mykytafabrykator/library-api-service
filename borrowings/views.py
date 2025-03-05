from django.db import transaction
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter
)
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingRetrieveSerializer,
    BorrowingReturnSerializer
)


class BorrowingsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (Borrowing.objects.select_related("book", "user")
                    .prefetch_related("payments"))

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
        if self.action == "return_book":
            return BorrowingReturnSerializer

        return BorrowingListSerializer

    @extend_schema(
        description=(
            "Marks the book as returned by setting the `actual_return_date`."
        ),
        request=BorrowingReturnSerializer,
        responses={
            200: OpenApiResponse(
                response={"message": "Book successfully returned!"},
                description="The book was successfully returned."
            ),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(
                description="Not authorized to return this book"
            ),
            404: OpenApiResponse(description="Borrowing not found"),
        },
        parameters=[
            OpenApiParameter(
                name="actual_return_date",
                description=(
                    "Optional. The date when the book was actually returned. "
                    "If not provided, today's date will be used."
                ),
                required=False,
                type=str,
            )
        ]
    )
    @action(detail=True, methods=["POST"], url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(
            borrowing,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save()

        return Response(
            {"message": "Book successfully returned!"},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="is_active",
                description="Filter borrowings by active status. "
                            "Use `true` for active (not returned) borrowings, "
                            "or `false` for returned borrowings.",
                required=False,
                type=bool
            ),
            OpenApiParameter(
                name="user_id",
                description=(
                    "Filter borrowings by user ID (admin only). "
                    "If omitted, returns all users' borrowings (for admins)."
                ),
                required=False,
                type=int
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
