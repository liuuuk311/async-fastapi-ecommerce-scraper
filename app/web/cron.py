import asyncio

from aiocron import crontab

from web.core.config import settings
from web.logger import get_logger
from web.tasks.notifications import (  # noqa
    notify_price_change_from_favorite_products,
    report_affiliated_clicks,
)
from web.tasks.product import (  # noqa
    europe_update,
    america_update,
    asia_update,
    oceania_update,
    america_import,
    europe_import,
    asia_import,
    oceania_import,
)

logger = get_logger(__name__)


@crontab("*/1 * * * *", start=True)  # At every minute
async def test_cron_job():
    logger.info("cron.py health check")


if __name__ == "__main__":
    logger.info(f"Running {__file__} in {settings.ENV}")
    asyncio.get_event_loop().run_forever()
