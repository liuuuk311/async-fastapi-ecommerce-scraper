import asyncio
import logging

from async_cron.job import CronJob
from async_cron.schedule import Scheduler

from web.tasks.store import import_products, update_products

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


jobs_to_schedule = [
    # Search and import
    CronJob(name='europe-import')
    .every(2)
    .monthday(1)
    .at('02:30')
    .go(import_products, continent_name="Europe"),
    CronJob(name='america-import')
    .every(2)
    .monthday(1)
    .at('07:30')
    .go(import_products, continent_name="America"),
    CronJob(name='asia-import')
    .every(2)
    .monthday(1)
    .at('15:30')
    .go(import_products, continent_name="Asia"),
    CronJob(name='oceania-import')
    .every(2)
    .monthday(1)
    .at('17:30')
    .go(import_products, continent_name="Oceania"),

    # Update products
    CronJob(name='europe-import')
    .every(1)
    .day
    .at('02:30')
    .go(update_products, continent_name="Europe"),
    CronJob(name='america-import')
    .every(1)
    .day
    .at('07:30')
    .go(update_products, continent_name="America"),
    CronJob(name='asia-import')
    .every(1)
    .day
    .at('15:30')
    .go(update_products, continent_name="Asia"),
    CronJob(name='oceania-import')
    .every(1)
    .day
    .at('17:30')
    .go(update_products, continent_name="Oceania"),
]


def main():
    job_scheduler = Scheduler(locale="en_US")

    for job in jobs_to_schedule:
        job_scheduler.add_job(job)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(job_scheduler.start())
    except KeyboardInterrupt:
        print('exit')


if __name__ == '__main__':
    main()
