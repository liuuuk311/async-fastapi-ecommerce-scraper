from decimal import Decimal
from typing import List, Dict, Union, Optional
from urllib.parse import urljoin, quote, urlencode

import aiohttp
from aiohttp import ClientConnectorError
from jinja2 import Environment, PackageLoader, select_autoescape
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from web.core.config import settings
from web.logger import get_logger
from web.models.product import Product
from web.models.user import User, UserSettings

logger = get_logger(__name__)


class EmailNotification:
    SEND_URL = "https://api.resend.com/emails"

    jinja2_env = Environment(
        loader=PackageLoader("web", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    SUBJECT_RESET_PASSWORD = "reset_password"
    SUBJECT_VERIFY_EMAIL = "verify_email"
    SUBJECT_PRICE_DROP_ALERT = "price_drop_alert"
    SUBJECTS = {
        "en": {
            SUBJECT_RESET_PASSWORD: "Reset your password",
            SUBJECT_VERIFY_EMAIL: "Verify you email",
            SUBJECT_PRICE_DROP_ALERT: "Price drop alert",
        },
        "it": {
            SUBJECT_RESET_PASSWORD: "Reimposta la tua password",
            SUBJECT_VERIFY_EMAIL: "Verifica il tuo indirizzo email",
            SUBJECT_PRICE_DROP_ALERT: "Il prezzo di un prodotto è sceso",
        },
    }

    def __init__(self, db: AsyncSession, *, user: User, force: bool = False):
        self.db = db
        self.user = user
        self.force = force

    async def get_user_settings(self) -> Optional[UserSettings]:
        stmt = select(UserSettings).where(UserSettings.user_id == self.user.id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def send(self, *, subject: str, template_name: str, **kwargs):
        await self.db.refresh(self.user)
        user_settings = await self.get_user_settings()

        to = self.user.email
        if not self.force and not user_settings:
            logger.warning(f"Skipping email. No settings for {to}")
            return

        if (
            not self.force
            and not user_settings.send_email_notifications
            and kwargs.get("is_notification", False)
        ):
            logger.warning("Skipping email. User does not want email notifications")
            return

        subject = self.SUBJECTS.get(user_settings.language, "en")[subject]
        payload = {
            "to": [to],
            "from": f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>",
            "subject": subject,
            "html": self.render(
                to_address=to,
                subject=subject,
                template_name=template_name,
                lang=user_settings.language,
                **kwargs,
            ),
        }

        if not settings.IS_PROD:
            logger.debug(f"Preventing to send email '{subject}' to {to} with {kwargs}")
            return

        async with aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            }
        ) as session:
            try:
                async with session.post(self.SEND_URL, json=payload) as resp:
                    logger.debug((await resp.text()))
            except ClientConnectorError:
                pass

    def render(self, template_name: str, lang: str = "en", **kwargs):
        template_name = (
            f"{lang}/{template_name}"
            if lang in settings.LANGUAGES
            else f"en/{template_name}"
        )
        template = self.jinja2_env.get_template(template_name)
        return template.render(project_name=settings.PROJECT_NAME, **kwargs)

    async def send_reset_password(self, *, token: str):
        return await self.send(
            subject=self.SUBJECT_RESET_PASSWORD,
            template_name="reset_password.html",
            cta_url=urljoin(settings.FRONTEND_HOST, f"reset-password/{token}"),
        )

    async def send_email_verification(self, *, code: str):
        params = urlencode({"code": code, "email": quote(self.user.email)})
        return await self.send(
            subject=self.SUBJECT_VERIFY_EMAIL,
            template_name="email_verification.html",
            cta_url=urljoin(settings.FRONTEND_HOST, f"verify?{params}"),
            code=code,
        )

    async def send_price_changed_in_favorite_product(
        self, *, products: List[Dict[str, Union[Product, Decimal]]]
    ):
        return await self.send(
            subject=self.SUBJECT_PRICE_DROP_ALERT,
            template_name="product_price_changed.html",
            products=products,
            is_notification=True,
        )
