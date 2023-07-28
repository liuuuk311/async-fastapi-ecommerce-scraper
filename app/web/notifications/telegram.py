import logging
import os
from urllib.parse import quote

import aiohttp

API_KEY = os.environ.get("TELEGRAM_BOT_API_KEY")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
API_URL = f"https://api.telegram.org/bot{API_KEY}/sendMessage?chat_id={CHAT_ID}&text="


FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_log_to_telegram(message: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL + quote(message)) as resp:
            logger.debug(await resp.text())
