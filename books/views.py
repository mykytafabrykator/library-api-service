from django.db import transaction
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter
)
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

from books.models import Book
from books.permissions import IsAdminOrReadOnly
from books.serializers import BookSerializer
from borrowings.utils import send_borrowing_notification
from borrowings.serializers import BorrowingCreateSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "borrow_book":
            return BorrowingCreateSerializer

        return BookSerializer

    @extend_schema(
        description=(
            "Creates a new borrowing record for the given book. "
            "A Stripe payment session will be automatically created, "
            "and the inventory of the book will be decreased by 1. "
            "A notification about the borrowing will also "
            "be sent to the Telegram channel."
        ),
        request=BorrowingCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=BorrowingCreateSerializer,
                description="Borrowing successfully created."
            ),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(
                description="Not authorized to borrow this book"
            ),
            404: OpenApiResponse(description="Book not found"),
        },
        parameters=[
            OpenApiParameter(
                name="borrow_date",
                description="The date when the book "
                            "is borrowed (format: YYYY-MM-DD)",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="expected_return_date",
                description="The expected return date "
                            "of the book (format: YYYY-MM-DD)",
                required=True,
                type=str,
            ),
        ],
    )
    @action(
        detail=True,
        methods=["POST"],
        url_path="borrow",
        permission_classes=[IsAuthenticated]
    )
    def borrow_book(self, request, pk=None):
        """Endpoint for borrowing a book."""
        book = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request, "book": book},
        )

        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            borrowing = serializer.save(user=request.user, book=book)

        send_borrowing_notification(borrowing)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
