from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from web.crud.product import ProductManager
from web.crud.store import StoreManager
from web.db import engine
from web.logger import get_logger
from web.models.product import FIELDS_TO_UPDATE, PriceHistory
from web.notifications.telegram import send_log_to_telegram
from web.tasks.scraper import (
    StoreScraper,
    ProductPriceNotFound,
    ProductNameNotFound,
    URLNotFound,
)

logger = get_logger(__name__)


async def update_products(continent_name: str):
    """Update all products stored"""
    logger.info(f"Started updating products for stores in {continent_name}")
    async with AsyncSession(engine, expire_on_commit=False) as db:
        stores = await StoreManager.get_active_stores(db, continent_name=continent_name)
        products_updated = 0
        for store in stores:
            store_products = await ProductManager.get_products_to_update(
                db, store_id=store.id
            )

            logger.debug(f"Updating products for {store.name}")
            products_updated += len(store_products)
            store_scraper = StoreScraper(db, store=store)
            for product in store_products:
                logger.debug(f"Current product {product.id}")
                product_link = store.affiliate_link(product.link)
                try:
                    new_data = await store_scraper.scrape(
                        product.link, FIELDS_TO_UPDATE
                    )
                except (URLNotFound, ProductNameNotFound, ProductPriceNotFound) as e:
                    logger.warning(f"DEACTIVATING PRODUCT! {e}")
                    await ProductManager.deactivate(db, product_link=product_link)
                    continue
                except Exception as e:
                    msg = f"Unexpected error when creating or updating product {product_link}: {e}"
                    await send_log_to_telegram(msg, 'error')
                    continue

                product = await ProductManager.update(
                    db, product=product, new_data=new_data, fields=FIELDS_TO_UPDATE
                )
                logger.info(f"Updated product: {product.id}")
                db.add(
                    PriceHistory(product_id=product.id, price=product.price)
                )  # Track historic price
                store.last_check = datetime.utcnow()
                await db.commit()

        if products_updated == 0:
            logger.info(f"No products to update for {continent_name}")
            return

        msg = (
            f"Update process finished for {continent_name} for {len(stores)} stores. "
            f"Updated {products_updated} products in total."
        )
        await send_log_to_telegram(msg)
