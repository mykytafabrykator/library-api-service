from celery import shared_task
from celery.schedules import crontab
from borrowings.models import Borrowing
from borrowings.utils import send_telegram_message
from django.utils.timezone import now

from library.celery import app


app.conf.beat_schedule = {
    "check-overdue-borrowings-daily": {
        "task": "borrowings.tasks.check_overdue_borrowings",
        "schedule": crontab(hour=0, minute=0),
    },
}


@shared_task
def check_overdue_borrowings():
    """Check for overdue borrowings and send notifications."""
    today = now().date()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today,
        actual_return_date__isnull=True
    )

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            message = (
                f"🚨 <b>Overdue Borrowing Alert!</b>\n\n"
                f"👤 User: {borrowing.user.first_name} "
                f"{borrowing.user.last_name} (email: {borrowing.user.email})\n"
                f"📚 Book: {borrowing.book.title}\n"
                f"📅 Expected Return Date: {borrowing.expected_return_date}\n"
                f"🆔 Borrowing ID: {borrowing.id}"
            )
            send_telegram_message(message)
    else:
        send_telegram_message("✅ No borrowings overdue today!")
