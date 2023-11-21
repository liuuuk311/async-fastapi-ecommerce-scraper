from typing import List

from sqlalchemy import distinct, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.sql.expression import SelectOfScalar

from web.logger import get_logger
from web.models.geo import Country, Continent
from web.models.store import Store

logger = get_logger(__name__)


class GeoManager:
    @staticmethod
    async def get_countries_with_active_stores(
        db: AsyncSession, *, limit: int, skip: int
    ) -> List[Country]:
        stmt: SelectOfScalar[Country] = (  # noqa
            select(Country)
            .join(Store)
            .where(Store.is_active.is_(True), Store.is_parsable.is_(True))
            .order_by(Country.name)
            .distinct(Country.name)
            .offset(skip)
            .limit(limit)
        )
        return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def get_continents_with_active_stores(
        db: AsyncSession, *, limit: int, skip: int
    ) -> List[Continent]:
        stmt: SelectOfScalar[Continent] = (  # noqa
            select(Continent)
            .join(Country)
            .join(Country.stores)
            .order_by(Continent.name)
            .distinct(Continent.name)
            .offset(skip)
            .limit(limit)
        )
        return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def get_countries_and_active_stores(db: AsyncSession) -> List[Country]:
        """Return the list of countries with a list of active stores for that country"""

        stmt: SelectOfScalar[Country] = (
            select(Country)
            .join(Store)
            .where(Store.is_active.is_(True), Store.is_parsable.is_(True))
            .options(selectinload(Country.stores))
            .distinct(Country.name)
            .order_by(Country.name)
        )
        logger.debug(stmt)
        return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def count_countries_with_active_store(db: AsyncSession) -> int:
        stmt = select(func.count(distinct(Store.country_id))).where(
            Store.is_active.is_(True), Store.is_parsable.is_(True)
        )
        return (await db.execute(stmt)).scalar_one()
