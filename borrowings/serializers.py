from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="title"
    )
    user = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="email"
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "user"
        )


class BorrowingRetrieveSerializer(BorrowingListSerializer):
    book = BookSerializer(read_only=True)


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("book", "borrow_date", "expected_return_date")

    def validate(self, data):
        book = data.get("book")
        borrow_date = data.get("borrow_date")
        expected_return_date = data.get("expected_return_date")

        if book.inventory <= 0:
            raise serializers.ValidationError(
                {"book": "This book is not available for borrowing."}
            )

        Borrowing.validate_borrowing(
            borrow_date=borrow_date,
            expected_return_date=expected_return_date,
        )

        return data
