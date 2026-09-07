import logging
import httpx
from app.config import settings

logger = logging.getLogger("chargehub.telegram")


def send_telegram_message(chat_id: str, text: str) -> bool:
    if not settings.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN not set, skipping send")
        return False
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        response = httpx.post(url, json={"chat_id": chat_id, "text": text}, timeout=10.0)
        data = response.json()
        if response.status_code == 200 and data.get("ok"):
            return True
        logger.error("Telegram API error: %s", data.get("description", "unknown"))
        return False
    except Exception as exc:
        logger.error("Telegram send failed: %s", exc)
        return False
