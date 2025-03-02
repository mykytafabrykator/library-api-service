from django.utils.timezone import now
from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing
from payments.utils import create_stripe_session


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
    payments = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="session_url"
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "user",
            "payments"
        )


class BorrowingRetrieveSerializer(BorrowingListSerializer):
    book = BookSerializer(read_only=True)


class BorrowingCreateSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    payments = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="session_url"
    )

    class Meta:
        model = Borrowing
        fields = ("id", "book", "borrow_date", "expected_return_date", "payments")

    def validate(self, data):
        book = self.context["book"]
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

    def create(self, validated_data):
        book = validated_data["book"]

        book.inventory -= 1
        book.save(update_fields=["inventory"])

        borrowing = Borrowing.objects.create(**validated_data)

        create_stripe_session(borrowing)

        return borrowing


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
