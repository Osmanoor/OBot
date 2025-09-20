import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Admin Credentials
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "password")

    # Marketdata.app API Token
    MARKETDATA_API_TOKEN: str = os.getenv("MARKETDATA_API_TOKEN")

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID")

    # Profit Goals (as percentages)
    GOAL_1_PERCENT: float = float(os.getenv("GOAL_1_PERCENT", 30.0))
    GOAL_2_PERCENT: float = float(os.getenv("GOAL_2_PERCENT", 60.0))
    GOAL_3_PERCENT: float = float(os.getenv("GOAL_3_PERCENT", 90.0))
    GOAL_4_PERCENT: float = float(os.getenv("GOAL_4_PERCENT", 120.0))
    GOAL_5_PERCENT: float = float(os.getenv("GOAL_5_PERCENT", 150.0))

    # Stop Loss (as a percentage of entry price)
    STOP_LOSS_PERCENT: float = float(os.getenv("STOP_LOSS_PERCENT", 50.0))

    # Database URL - defaults to a local file, can be overridden for Docker
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///trades.db")

    # Report Configuration
    BACKGROUND_IMAGE_PATH: str = "app/static/background.jpg"
    BOT_NAME: str = os.getenv("BOT_NAME", "Option Bot")

    # Pyppeteer Configuration
    CHROME_EXECUTABLE_PATH: str = os.getenv("CHROME_EXECUTABLE_PATH") or None


# Instantiate settings
settings = Settings()

# Basic validation
if not settings.MARKETDATA_API_TOKEN or not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
    raise ValueError("API tokens and Chat ID must be set in the .env file.")
