from _decimal import Decimal
from typing import List, Optional

from sqlalchemy import asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from web.models.geo import Country, Continent
from web.models.shipping import ShippingMethod
from web.models.store import Store


class StoreManager:
    @classmethod
    async def get_active_stores(
        cls, db: AsyncSession, *, continent_name: str
    ) -> List[Store]:
        stmt = (
            select(Store)
            .join(Country)
            .join(Continent)
            .where(
                Store.is_parsable.is_(True),
                Store.is_active.is_(True),
                Continent.name == continent_name,
            )
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
