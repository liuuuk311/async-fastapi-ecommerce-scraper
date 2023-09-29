from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import selectinload

from web.db import engine
from web.logger import get_logger
from web.models.geo import Country, Continent
from web.models.import_query import ImportQuery
from web.models.product import Product, FIELDS_TO_UPDATE
from web.models.store import Store
from sqlalchemy import desc, func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from web.models.tracking import ClickedProduct
from web.notifications.telegram import send_log_to_telegram

logger = get_logger(__name__)


async def import_products(
    continent_name: str, limit_search_results: Optional[int] = None
):
    """For all stores search all import queries and create or update the products"""
    logger.info(f"Started importing products for stores in {continent_name}")
    # Expire on commit: https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#asyncio-orm-avoid-lazyloads
    async with AsyncSession(engine, expire_on_commit=False) as session:
        stores = (
            (
                await session.execute(
                    select(Store)
                    .join(Country)
                    .join(Continent)
                    .where(
                        Store.is_parsable.is_(True),
                        Store.is_active.is_(True),
                        Continent.name == continent_name,
                    )
                )
            )
            .scalars()
            .all()
        )
        import_queries = (
            (
                await session.execute(
                    select(ImportQuery)
                    .where(ImportQuery.is_active.is_(True))
                    .order_by(desc(ImportQuery.priority_score))
                )
            )
            .scalars()
            .all()
        )

        logger.info(
            f"Performing import on {len(import_queries)} search queries across {len(stores)} stores"
        )
        for query in import_queries:
            for store in stores:
                await store.search_and_import_products(
                    session, query, limit_search_results=limit_search_results
                )

        msg = f"Import process finished for {continent_name} for {len(stores)} stores with {len(import_queries)} queries"
        logger.info(msg)
        await send_log_to_telegram(msg)


async def update_products(
    continent_name: str
):
    """ Update all products stored """
    logger.info(f"Started updating products for stores in {continent_name}")
    async with AsyncSession(engine, expire_on_commit=False) as session:
        stores = (
            (
                await session.execute(
                    select(Store)
                    .join(Country)
                    .join(Continent)
                    .where(
                        Store.is_parsable.is_(True),
                        Store.is_active.is_(True),
                        Continent.name == continent_name,
                    )
                )
            )
            .scalars()
            .all()
        )
        logger.debug(f"{[s.name for s in stores]}")
        products_updated = 0
        for store in stores:
            store_products = (
                (
                    await session.execute(
                        select(Product)
                        .join(Store)
                        .outerjoin(ClickedProduct)
                        .where(
                            Store.id == store.id,
                            Product.import_date + timedelta(hours=4) <= datetime.now(),
                            Product.is_active.is_(True),
                        )
                        .options(selectinload(Product.import_query))
                        .group_by(Product.id, Product.import_date)
                        .order_by(
                            func.coalesce(func.count(ClickedProduct.id), 0).desc(),
                            Product.import_date.asc()
                        )
                    )
                )
                .scalars()
                .all()
            )
            logger.debug(f"Updating products for {store.name}")
            products_updated += len(store_products)
            for product in store_products:
                logger.debug(f"Current product {product.id}")
                await store.create_or_update_product(
                    session, product.link, product.import_query, FIELDS_TO_UPDATE
                )

        if products_updated == 0:
            return

        msg = (
            f"Update process finished for {continent_name} for {len(stores)} stores. "
            f"Updated {products_updated} products in total."
        )
        logger.info(msg)
        await send_log_to_telegram(msg)


async def check_store_compatibility(store_pks: List[int]):
    async with AsyncSession(engine, expire_on_commit=False) as session:
        stores = (
            await session.execute(select(Store).where(Store.id.in_(store_pks)))
        ).scalars()
        for store in stores:
            await store.check_compatibility(session)
