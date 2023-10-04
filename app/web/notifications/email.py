import aiohttp
from aiohttp import ClientConnectorError

from web.core.config import settings
from web.logger import get_logger

logger = get_logger(__name__)


class EmailNotification:
    SEND_URL = "https://api.resend.com/emails"

    @classmethod
    async def send(cls, *, to: str, subject: str, html: str):
        payload = {
            "to": [to],
            "from": f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>",
            "subject": subject,
            "html": html,
        }
        async with aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            }
        ) as session:
            try:
                async with session.post(cls.SEND_URL, json=payload) as resp:
                    logger.debug(resp.text())
            except ClientConnectorError:
                pass

    @classmethod
    async def send_reset_password(cls, *, to: str, token: str):
        logger.debug(f"Sending email to {to} for resetting the password: {token}")
        # return await cls.send(to=to, subject="Reset your password")
