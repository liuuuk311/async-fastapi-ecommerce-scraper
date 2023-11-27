from sqlalchemy.ext.asyncio import AsyncSession

from web.manager.store import StoreManager
from web.db import engine
from web.logger import get_logger
from web.notifications.telegram import send_log_to_telegram
from web.tasks.product import ProductImporter
from web.tasks.scraper import (
    StoreScraper,
)

logger = get_logger(__name__)


async def check_stores_with_low_product_count():
    async with AsyncSession(engine, expire_on_commit=False) as db:
        stores = await StoreManager.get_stores_with_less_than_n_products(db, n=20)
        for store in stores:
            store_scraper = StoreScraper(store=store)
            success, error_message = await store_scraper.ping_website()

            if not success:
                await send_log_to_telegram(
                    f"Check for {store.name} failed. "
                    f"Could not reach the website. {error_message}"
                )
                store.is_parsable = False
                store.reason_could_not_be_parsed = error_message
                await db.commit()
                continue  # Nothing else to do, skip to the next store

            # Can we import new products?
            importer = ProductImporter(db, store=store)
            await importer.import_product(limit=20)

            if importer.link_processed > 0 and importer.products_created_or_update < 20:
                store.is_parsable = False
                store.reason_could_not_be_parsed = "Cannot import new products"
                await db.commit()
                await send_log_to_telegram(
                    f"ACTION REQUIRED: {store.name} has been deactivated because "
                    f"it was not possible to import new products"
                )
