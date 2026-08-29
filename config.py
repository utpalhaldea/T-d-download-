import os
from dotenv import load_dotenv

load_dotenv()


def get_int(name: str, default: int = 0) -> int:
    value = os.getenv(name, "").strip()

    if not value:
        return default

    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{name} must be an integer")


BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
APP_ID = get_int("APP_ID")
API_HASH = os.getenv("API_HASH", "").strip()

STORAGE_GROUP_ID = get_int("STORAGE_GROUP_ID")
ADMIN_ID = get_int("ADMIN_ID")

PORT = get_int("PORT", 8000)

THIRD_PARTY_TERABOXDL_URL = os.getenv(
    "THIRD_PARTY_TERABOXDL_URL", ""
).strip()

PROXY_URL = os.getenv("PROXY_URL", "").strip()

DISKWALA_PROXY_URL = os.getenv(
    "DISKWALA_PROXY_URL", ""
).strip()

DISKWALA_API_KEY = os.getenv(
    "DISKWALA_API_KEY", ""
).strip()


def validate_telegram_config():
    missing = []

    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")

    if not APP_ID:
        missing.append("APP_ID")

    if not API_HASH:
        missing.append("API_HASH")

    if missing:
        raise RuntimeError(
            "Missing environment variables: "
            + ", ".join(missing)
        )
