import asyncio
import logging

from async_cron.job import CronJob
from async_cron.schedule import Scheduler

from web.notifications.telegram import send_log_to_telegram
from web.tasks.store import import_products, update_products


FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT, level=loggin.DEBUG)
logger = logging.getLogger(__name__)



jobs_to_schedule = [
    # Search and import
    CronJob(name='europe-import', tolerance=30)
    .every(1)
    .monthday(1)
    .at('02:30')
    .go(import_products, continent_name="Europe"),
    CronJob(name='america-import', tolerance=30)
    .every(1)
    .monthday(5)
    .at('07:30')
    .go(import_products, continent_name="America"),
    CronJob(name='asia-import', tolerance=30)
    .every(1)
    .monthday(10)
    .at('15:30')
    .go(import_products, continent_name="Asia"),
    CronJob(name='oceania-import', tolerance=30)
    .every(1)
    .monthday(15)
    .at('17:30'),

    CronJob(name='europe-import-2', tolerance=30)
    .every(1)
    .monthday(16)
    .at('02:30')
    .go(import_products, continent_name="Europe"),
    CronJob(name='america-import-2', tolerance=30)
    .every(1)
    .monthday(20)
    .at('07:30')
    .go(import_products, continent_name="America"),
    CronJob(name='asia-import-2', tolerance=30)
    .every(1)
    .monthday(25)
    .at('15:30')
    .go(import_products, continent_name="Asia"),
    CronJob(name='oceania-import-2', tolerance=30)
    .every(1)
    .monthday(28)
    .at('17:30')
    .go(import_products, continent_name="Oceania"),

    # Update products
    CronJob(name='europe-update').every(4).hour.go(update_products, continent_name="Europe"),
    CronJob(name='america-update').every(4).hour.go(update_products, continent_name="America"),
    CronJob(name='asia-update').every(4).hour.go(update_products, continent_name="Asia"),
    CronJob(name='oceania-update').every(4).hour.go(update_products, continent_name="Oceania"),
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
    except Exception as e:
        send_log_to_telegram(str(e))
        raise e


if __name__ == '__main__':
    main()
