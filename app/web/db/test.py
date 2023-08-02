import logging

from web.core.config import settings
from web.db import engine
from sqlalchemy import func
from sqlmodel.ext.asyncio.session import AsyncSession
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(settings.MAX_RETRIES_SECONDS),
    wait=wait_fixed(settings.WAIT_SECONDS),
    before=before_log(logger, logging.DEBUG),
    after=after_log(logger, logging.WARN),
)
async def test_db_connection() -> None:
    logger.info(f"Testing connection on {settings.DATABASE_URI}")
    async with AsyncSession(engine) as session:
        try:
            # Try to create session to check if DB is awake
            await session.execute(func.text("SELECT 1"))
        except Exception as e:
            logger.error(e)
            raise e
        finally:
            await session.close()
