from django.db import transaction
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
