from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from playwright.async_api import TimeoutError

from web.manager.product import ProductManager
from web.manager.store import StoreManager
from web.db import engine
from web.logger import get_logger
from web.models.product import FIELDS_TO_UPDATE, FIELDS_TO_IMPORT, Product
from web.models.store import Store
from web.notifications.telegram import send_log_to_telegram
from web.tasks.scraper import (
    StoreScraper,
    ProductPriceNotFound,
    ProductNameNotFound,
    URLNotFound,
    SiteMapScraper,
)

logger = get_logger(__name__)


async def scrape_or_deactivate(
    db: AsyncSession, scraper: StoreScraper, url: str, fields: List
) -> Optional[Product]:
    try:
        return await scraper.scrape(url, fields)
    except (URLNotFound, ProductNameNotFound, ProductPriceNotFound, TimeoutError) as e:
        logger.warning(f"DEACTIVATING PRODUCT! {e}")
        await ProductManager.deactivate(db, product_link=url)
        return
    except Exception as e:
        msg = f"Unexpected error when creating or updating product {url}: {e}"
        await send_log_to_telegram(msg, "error")
        return


async def update_products_by_continent(continent_name: str):
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
            store_scraper = StoreScraper(store=store)
            for product in store_products:
                logger.debug(f"Current product {product.id}")
                product_link = store.affiliate_link(product.link)
                new_data = await scrape_or_deactivate(
                    db, store_scraper, product_link, FIELDS_TO_UPDATE
                )

                if not new_data:
                    continue

                product = await ProductManager.update(
                    db, product=product, new_data=new_data, fields=FIELDS_TO_UPDATE
                )
                logger.info(f"Updated product: {product.id}")
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


async def import_products_by_continent(continent_name: str):
    """For all stores search all import queries and create or update the products"""
    logger.info(f"Started importing products for stores in {continent_name}")
    # Expire on commit:
    # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#asyncio-orm-avoid-lazyloads
    async with AsyncSession(engine, expire_on_commit=False) as db:
        stores = await StoreManager.get_active_stores(db, continent_name=continent_name)
        link_processed = 0
        products_created_or_update = 0

        for store in stores:
            importer = ProductImporter(db, store=store)
            await importer.import_product(limit=500)
            link_processed += importer.link_processed
            products_created_or_update += importer.products_created_or_update

        msg = (
            f"Import process finished for {continent_name} "
            f"for {len(stores)} stores. "
            f"Created or updated {products_created_or_update} products "
            f"and processed {link_processed} links"
        )
        await send_log_to_telegram(msg)


class ProductImporter:
    def __init__(self, db: AsyncSession, *, store: Store):
        self.store = store
        self.db = db
        self.link_processed = 0
        self.products_created_or_update = 0

    async def import_product(self, limit: Optional[int] = None):
        if not self.store.sitemaps:
            await send_log_to_telegram(
                f"ACTION REQUIRED: Skipping import from '{self.store.name}' because "
                f"it does not have sitemaps, please add one or deactivate the store"
            )
            return

        product_links = await SiteMapScraper().scrape(self.store.sitemaps, limit=limit)
        if not product_links:
            logger.warning(f"Could not find any product links from the sitemaps")
            return

        self.link_processed += len(product_links)
        store_scraper = StoreScraper(store=self.store)

        for product_link in product_links:
            product_data = await scrape_or_deactivate(
                self.db, store_scraper, product_link, FIELDS_TO_IMPORT
            )
            if not product_data:
                continue

            await ProductManager.create_or_update(
                self.db, store=self.store, data=product_data
            )
            self.products_created_or_update += 1
