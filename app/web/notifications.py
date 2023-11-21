import asyncio

from async_cron.job import CronJob
from async_cron.schedule import Scheduler

from web.core.config import settings
from web.logger import get_logger
from web.notifications.telegram import send_log_to_telegram, post_used_product
from web.tasks.notifications import (
    report_affiliated_clicks,
    notify_price_change_from_favorite_products,
)

logger = get_logger(__name__)


jobs_to_schedule = [
    # Reports
    CronJob(name="report-affiliated-clicks", tolerance=30)
    .every(1)
    .day.at("17:30")
    .go(report_affiliated_clicks),
    CronJob(name="price-drop-alert-favorite-products", tolerance=30)
    .every(1)
    .day.at("18:00")
    .go(notify_price_change_from_favorite_products),
]


def main():
    job_scheduler = Scheduler(locale="en_US")

    for job in jobs_to_schedule:
        job_scheduler.add_job(job)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(job_scheduler.start())
    except KeyboardInterrupt:
        print("exit")
    except Exception as e:
        send_log_to_telegram(str(e), "error")
        raise e


def test():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(post_used_product("FPV finder test"))
    except KeyboardInterrupt:
        print("exit")


if __name__ == "__main__":
    logger.info(f"Running {__file__} in {settings.ENV}")
    if settings.IS_PROD:
        main()
    else:
        test()
