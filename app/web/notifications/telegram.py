import os
from urllib.parse import quote

import aiohttp

from web.core.config import settings
from web.logger import get_logger

API_KEY = os.environ.get("TELEGRAM_BOT_API_KEY")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
API_URL = f"https://api.telegram.org/bot{API_KEY}/sendMessage?chat_id={CHAT_ID}&text="


logger = get_logger(__name__)


async def send_log_to_telegram(message: str, level: str = "info"):
    getattr(logger, level, "info")(message)

    if not settings.IS_PROD:
        logger.debug(f"Preventing Telegram message: {message}")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL + quote(message)) as resp:
            logger.debug(await resp.text())
