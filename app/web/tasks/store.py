import logging
from typing import List, Optional

from sqlalchemy.orm import selectinload

from web.db import engine
from web.models.geo import Country, Continent
from web.models.import_query import ImportQuery
from web.models.product import Product, FIELDS_TO_UPDATE
from web.models.store import Store
from sqlalchemy import desc
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from web.notifications.telegram import send_log_to_telegram

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        for store in stores:
            store_products = (
                (
                    await session.execute(
                        select(Product)
                        .join(Store)
                        .where(
                            Store.id == store.id,
                        )
                        .options(selectinload(Product.import_query))
                    )
                )
                .scalars()
                .all()
            )
            for product in store_products:
                await store.create_or_update_product(
                    session, product.link, product.import_query, FIELDS_TO_UPDATE
                )

        msg = f"Update process finished for {continent_name} for {len(stores)} stores"
        logger.info(msg)
        await send_log_to_telegram(msg)


async def check_store_compatibility(store_pks: List[int]):
    async with AsyncSession(engine, expire_on_commit=False) as session:
        stores = (
            await session.execute(select(Store).where(Store.id.in_(store_pks)))
        ).scalars()
        for store in stores:
            await store.check_compatibility(session)
