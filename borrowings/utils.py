import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
API_URL_SEND_MESSAGE = (f"https://api.telegram.org/"
                        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage")


def send_telegram_message(text: str):
    """Send a message to the Telegram channel using the bot."""
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
    }

    response = requests.post(API_URL_SEND_MESSAGE, json=payload)

    if response.status_code != 200:
        raise Exception(f"Failed to send message: {response.text}")

    return response.json()


def send_borrowing_notification(borrowing):
    """Format and send a notification about a new borrowing."""
    message = (
        f"📖 <b>New Borrowing Created!</b>\n"
        f"👤 User: {borrowing.user.first_name} {borrowing.user.last_name} "
        f"(email: {borrowing.user.email})\n"
        f"📚 Book: {borrowing.book.title}\n"
        f"📅 Borrow Date: {borrowing.borrow_date}\n"
        f"📆 Expected Return: {borrowing.expected_return_date}\n"
        f"🆔 Borrowing ID: {borrowing.id}"
    )

    send_telegram_message(message)
