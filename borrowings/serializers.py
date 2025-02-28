from django.utils.timezone import now
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
        fields = ("id", "book", "borrow_date", "expected_return_date")

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


class BorrowingReturnSerializer(serializers.ModelSerializer):
    actual_return_date = serializers.DateField(required=False)

    class Meta:
        model = Borrowing
        fields = ("actual_return_date",)

    def validate(self, data):
        borrowing = self.instance
        actual_return_date = data.get("actual_return_date")

        if borrowing.actual_return_date is not None:
            raise serializers.ValidationError(
                {"actual_return_date": "This book has already been returned."}
            )

        Borrowing.validate_borrowing(
            borrow_date=borrowing.borrow_date,
            expected_return_date=borrowing.expected_return_date,
            actual_return_date=actual_return_date,
        )

        return data

    def update(self, instance, validated_data):
        instance.actual_return_date = validated_data.get(
            "actual_return_date",
            now().date()
        )

        book = instance.book
        book.inventory += 1
        book.save(update_fields=["inventory"])

        instance.save(update_fields=["actual_return_date"])
        return instance
