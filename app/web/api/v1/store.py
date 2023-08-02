import logging
from typing import List

from web.api import deps
from fastapi import APIRouter, Depends
from web.models.geo import Country
from web.models.product import Product
from web.models.schemas import StoreStats, StoreByCountryRead, ShippingMethodRead
from web.models.shipping import ShippingMethod
from web.models.store import Store, SuggestedStore
from sqlalchemy import distinct
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import count
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


logging.basicConfig(level=loggin.DEBUG)
logger = logging.getLogger(__name__)


@router.get("/stores/stats", response_model=StoreStats)
async def get_stats(db: AsyncSession = Depends(deps.get_db)):
    stores_count = (
        await db.execute(
            select(count(Store.id)).where(
                Store.is_active.is_(True), Store.is_parsable.is_(True)
            )
        )
    ).scalar_one()
    countries_count = (
        await db.execute(
            select(count(distinct(Store.country_id))).where(
                Store.is_active.is_(True), Store.is_parsable.is_(True)
            )
        )
    ).scalar_one()
    products_count = (
        await db.execute(
            select(count(Product.id))
            .join(Store)
            .where(
                Product.is_active.is_(True),
                Store.is_active.is_(True),
                Store.is_parsable.is_(True),
            )
        )
    ).scalar_one()
    return {
        'stores_count': stores_count,
        'products_count': products_count,
        'countries_count': countries_count,
    }


@router.get("/stores-by-country", response_model=List[StoreByCountryRead])
async def get_stats(db: AsyncSession = Depends(deps.get_db)):
    return (
        (
            await db.execute(
                select(Country)
                .join(Store)
                .where(Store.is_active.is_(True), Store.is_parsable.is_(True))
                .options(selectinload(Country.stores))
                .distinct(Country.name)
                .order_by(Country.name)
            )
        )
        .scalars()
        .all()
    )


@router.post("/stores/suggest")
async def suggest_new_store(
    suggested_store: SuggestedStore, db: AsyncSession = Depends(deps.get_db)
):
    db.add(suggested_store)
    await db.commit()
    return {'status': 'ok'}


@router.get(
    "/stores/{public_id}/shipping-methods", response_model=List[ShippingMethodRead]
)
async def get_shipping_method(
    public_id,
    db: AsyncSession = Depends(deps.get_db),
):
    stmt = (
        select(ShippingMethod)
        .join(Store)
        .where(
            Store.public_id == public_id,
            Store.is_active.is_(True),
            ShippingMethod.is_active.is_(True),
        )
        .order_by(ShippingMethod.price)
    )

    return (await db.execute(stmt)).scalars().all()
