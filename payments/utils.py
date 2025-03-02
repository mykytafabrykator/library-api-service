import stripe

from payments.models import Payment

SUCCESS_URL = "http://localhost:8000/api/v1/payments/"
CANCEL_URL = "http://localhost:8000/api/v1/payments/"


def create_stripe_session(borrowing):
    """
    Create a new Stripe Checkout Session for a Borrowing.
    """
    total_price = Payment.calculate_money_to_pay(borrowing)
    unit_amount = int(total_price * 100)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                        "description": f"From {borrowing.borrow_date} "
                                       f"to {borrowing.expected_return_date}",
                    },
                    "unit_amount": unit_amount,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=SUCCESS_URL,
        cancel_url=CANCEL_URL,
    )

    payment = Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=Payment.TypeChoices.PAYMENT,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_price,
    )

    return payment
