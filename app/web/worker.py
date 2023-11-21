import asyncio

from async_cron.job import CronJob
from async_cron.schedule import Scheduler

from web.core.config import settings
from web.logger import get_logger
from web.notifications.telegram import send_log_to_telegram
from web.tasks.notifications import (
    report_affiliated_clicks,
    notify_price_change_from_favorite_products,
)
from web.tasks.product import update_products_by_continent, import_products_by_continent
from web.tasks.store import check_stores_with_low_product_count

logger = get_logger(__name__)


jobs_to_schedule = [
    # Search and import
    CronJob(name="europe-import", tolerance=30)
    .every(4)
    .day.at("02:30")
    .go(import_products_by_continent, continent_name="Europe"),
    CronJob(name="america-import", tolerance=30)
    .every(4)
    .day.at("07:30")
    .go(import_products_by_continent, continent_name="America"),
    CronJob(name="asia-import", tolerance=30)
    .every(4)
    .day.at("15:30")
    .go(import_products_by_continent, continent_name="Asia"),
    CronJob(name="oceania-import", tolerance=30)
    .every(4)
    .day.at("17:30")
    .go(import_products_by_continent, continent_name="Oceania"),
    # Update products
    CronJob(name="europe-update")
    .every(8)
    .hour.go(update_products_by_continent, continent_name="Europe"),
    CronJob(name="america-update")
    .every(8)
    .hour.go(update_products_by_continent, continent_name="America"),
    CronJob(name="asia-update")
    .every(8)
    .hour.go(update_products_by_continent, continent_name="Asia"),
    CronJob(name="oceania-update")
    .every(8)
    .hour.go(update_products_by_continent, continent_name="Oceania"),
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
        loop.run_until_complete(import_products_by_continent(continent_name="Europe"))
    except KeyboardInterrupt:
        print("exit")


if __name__ == "__main__":
    logger.info(f"Running {__file__} in {settings.ENV}")
    if settings.IS_PROD:
        main()
    else:
        test()
