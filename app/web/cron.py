import asyncio

from web.core.config import settings
from web.logger import get_logger

logger = get_logger(__name__)


if __name__ == "__main__":
    logger.info(f"Running {__file__} in {settings.ENV}")
    asyncio.get_event_loop().run_forever()
