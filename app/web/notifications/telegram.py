import os
from urllib.parse import quote

import aiohttp

from web.core.config import settings
from web.logger import get_logger


# Logger keys
API_KEY = os.environ.get("TELEGRAM_BOT_API_KEY")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# NorthFPV bot keys
NORTH_FPV_BOT_KEY = os.environ.get("TELEGRAM_NORTH_FPV_BOT_API_KEY")
NORTH_FPV_MAIN_CHANNEL = os.environ.get("TELEGRAM_NORTH_FPV_MAIN_CHANNEL")

LOG_API_URL = f"https://api.telegram.org/bot{API_KEY}/sendMessage?parse_mode=HTML&chat_id={CHAT_ID}&text="
USED_PRODUCTS_API_URL = f"https://api.telegram.org/bot{NORTH_FPV_BOT_KEY}/sendMessage?parse_mode=HTML&chat_id={NORTH_FPV_MAIN_CHANNEL}&text="


logger = get_logger(__name__)


USED_PRODUCT_AD = """
🎯 {title}

🔴 Condizioni: {conditions}
🚚 Spedizione: {shipping} 

👉 <a href="{link}">Contatta il venditore</a>
"""


async def send_log_to_telegram(message: str, level: str = "info"):
    getattr(logger, level, "info")(message)

    if not settings.IS_PROD:
        logger.debug(f"Preventing Telegram message: {message}")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(LOG_API_URL + quote(message)) as resp:
            logger.debug(await resp.text())


async def post_used_product(message: str):
    if not settings.IS_PROD:
        logger.debug(f"Preventing Telegram message: {message}")
        return

    logger.debug(f"Sending {message=}")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://api.telegram.org/bot{NORTH_FPV_BOT_KEY}/sendMessage",
            json={
                "chat_id": NORTH_FPV_MAIN_CHANNEL,
                "parse_mode": "HTML",
                "text": message,
            },
        ) as resp:
            logger.debug(await resp.text())
