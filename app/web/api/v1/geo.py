import logging
from typing import List

from fastapi import APIRouter, Depends
from web.models.geo import Country, CountryRead, ContinentRead, Continent
from web.models.store import Store
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from web.api import deps

router = APIRouter()


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@router.get("/countries", response_model=List[CountryRead])
async def get_countries(
    db: AsyncSession = Depends(deps.get_db), skip: int = 0, limit: int = 100
):
    return (
        (
            await db.execute(
                select(Country)
                .join(Store)
                .where(Store.is_active.is_(True), Store.is_parsable.is_(True))
                .order_by(Country.name)
                .distinct(Country.name)
                .offset(skip)
                .limit(limit)
            )
        )
        .scalars()
        .all()
    )


@router.get("/continents", response_model=List[ContinentRead])
async def get_continents(
    db: AsyncSession = Depends(deps.get_db), skip: int = 0, limit: int = 100
):
    return (
        (
            await db.execute(
                select(Continent)
                .join(Country)
                .join(Store)
                .where(Store.is_active.is_(True), Store.is_parsable.is_(True))
                .order_by(Continent.name)
                .distinct(Continent.name)
                .offset(skip)
                .limit(limit)
            )
        )
        .scalars()
        .all()
    )
