from _decimal import Decimal
from typing import List, Optional, Sequence

from sqlalchemy import asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from web.logger import get_logger
from web.models.geo import Country, Continent
from web.models.product import Product
from web.models.shipping import ShippingMethod
from web.models.store import Store

logger = get_logger(__name__)


class StoreManager:
    @classmethod
    async def get_active_stores(
        cls, db: AsyncSession, *, continent_name: str
    ) -> Sequence[Store]:
        stmt = (
            select(Store)
            .join(Country)
            .join(Continent)
            .where(
                Store.is_parsable.is_(True),
                Store.is_active.is_(True),
                Continent.name == continent_name,
            )
            .options(selectinload(Store.sitemaps))
        )
        return (await db.execute(stmt)).scalars().all()

    @classmethod
    async def get_best_shipping_method(
        cls, db: AsyncSession, *, store_id: int, product_price: Decimal
    ) -> Optional[ShippingMethod]:
        free_shipping_stmt = select(ShippingMethod).where(
            ShippingMethod.store_id == store_id,
            ShippingMethod.price.is_(None),
        )

        free_shipping = (await db.execute(free_shipping_stmt)).scalars().first()

        cheapest_shipping_method_stmt = (
            select(ShippingMethod)
            .where(ShippingMethod.store_id == store_id)
            .order_by(asc(ShippingMethod.price))
        )

        if not free_shipping:
            return (await db.execute(cheapest_shipping_method_stmt)).scalars().first()

        if (
            not free_shipping.min_price_shipping_condition
            or product_price >= free_shipping.min_price_shipping_condition
        ):
            return free_shipping

        return (await db.execute(cheapest_shipping_method_stmt)).scalars().first()

    @classmethod
    async def get_stores_with_less_than_n_products(
        cls, db: AsyncSession, *, n: int
    ) -> List[Store]:
        product_count_by_store_stmt = (
            select([Product.store_id, func.count(Product.id).label("count")])
            .where(Product.is_active.is_(True))
            .group_by(Product.store_id)
            .subquery()
        )
        stmt = (
            select(Store)
            .join(
                product_count_by_store_stmt,
                onclause=product_count_by_store_stmt.c.store_id == Store.id,
                isouter=True,
            )
            .options(selectinload(Store.sitemaps))
            .where(func.coalesce(product_count_by_store_stmt.c.count, 0) < n)
        )

        return (await db.execute(stmt)).scalars().all()
