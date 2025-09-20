import requests
from typing import Optional

from ..config import settings

class TelegramService:
    """
    A service to interact with the Telegram Bot API.
    """
    def __init__(self, bot_token: str, chat_id: str):
        if not bot_token or not chat_id:
            raise ValueError("Telegram Bot Token and Chat ID are required.")
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, text: str) -> bool:
        """
        Sends a text message to the configured chat ID.
        """
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("ok", False)
        except requests.exceptions.RequestException as e:
            print(f"Error sending Telegram message: {e}")
            return False

    def send_photo(self, photo_data: bytes, caption: Optional[str] = None) -> bool:
        """
        Sends a photo to the configured chat ID.
        
        Args:
            photo_data: The binary content of the photo.
            caption: Optional text to send with the photo.
        """
        url = f"{self.base_url}/sendPhoto"
        files = {"photo": ("image.png", photo_data, "image/png")}
        data = {"chat_id": self.chat_id}
        if caption:
            data["caption"] = caption

        try:
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            return response.json().get("ok", False)
        except requests.exceptions.RequestException as e:
            print(f"Error sending Telegram photo: {e}")
            return False

    def send_document(self, document_data: bytes, filename: str, caption: Optional[str] = None) -> bool:
        """
        Sends a document (e.g., PDF) to the configured chat ID.
        
        Args:
            document_data: The binary content of the file.
            filename: The name of the file (e.g., "report.pdf").
            caption: Optional text to send with the document.
        """
        url = f"{self.base_url}/sendDocument"
        files = {"document": (filename, document_data)}
        data = {"chat_id": self.chat_id}
        if caption:
            data["caption"] = caption

        try:
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            return response.json().get("ok", False)
        except requests.exceptions.RequestException as e:
            print(f"Error sending Telegram document: {e}")
            return False

# Create a single instance of the service to be used throughout the app
telegram_service = TelegramService(
    bot_token=settings.TELEGRAM_BOT_TOKEN,
    chat_id=settings.TELEGRAM_CHAT_ID
)