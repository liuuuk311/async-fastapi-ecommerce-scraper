import asyncio

from web.db.test import test_db_connection
from web.logger import get_logger

logger = get_logger(__name__)


async def main() -> None:
    logger.info("Initializing worker service")
    await test_db_connection()
    logger.info("Worker service finished initializing")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
