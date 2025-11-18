import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_GROUP_CHAT_ID: int = int(os.getenv("TELEGRAM_GROUP_CHAT_ID", "0"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "dev")

settings = Settings()
