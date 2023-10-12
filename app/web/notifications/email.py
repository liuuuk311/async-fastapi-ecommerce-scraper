from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientConnectorError
from jinja2 import Environment, PackageLoader, select_autoescape

from web.core.config import settings
from web.logger import get_logger

logger = get_logger(__name__)


class EmailNotification:
    SEND_URL = "https://api.resend.com/emails"

    jinja2_env = Environment(
        loader=PackageLoader("web", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    @classmethod
    async def send(cls, *, to: str, subject: str, template_name: str, **kwargs):
        payload = {
            "to": [to],
            "from": f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>",
            "subject": subject,
            "html": cls.render(
                to_address=to, subject=subject, template_name=template_name, **kwargs
            ),
        }
        async with aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            }
        ) as session:
            try:
                async with session.post(cls.SEND_URL, json=payload) as resp:
                    logger.debug((await resp.text()))
            except ClientConnectorError:
                pass

    @classmethod
    def render(cls, template_name: str, **kwargs):
        template = cls.jinja2_env.get_template(template_name)
        return template.render(project_name=settings.PROJECT_NAME, **kwargs)

    @classmethod
    async def send_reset_password(cls, *, to: str, token: str):
        return await cls.send(
            to=to,
            subject="Reset your password",
            template_name="reset_password.html",
            cta_url=urljoin(settings.FRONTEND_HOST, f"reset-password/{token}"),
            cta_label="Reset your password",
        )
