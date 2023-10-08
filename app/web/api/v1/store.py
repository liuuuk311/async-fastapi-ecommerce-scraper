from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.sql.functions import count
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from web.api import deps
from web.crud.geo import GeoManager
from web.logger import get_logger
from web.models.product import Product
from web.models.schemas import StoreStats, StoreByCountryRead, ShippingMethodRead
from web.models.shipping import ShippingMethod
from web.models.store import Store, SuggestedStore

router = APIRouter()


logger = get_logger(__name__)


@router.get("/stores/stats", response_model=StoreStats)
async def get_stats(db: AsyncSession = Depends(deps.get_db)):
    stores_count = (
        await db.execute(
            select(count(Store.id)).where(
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
        "stores_count": stores_count,
        "products_count": products_count,
        "countries_count": await GeoManager.count_countries_with_active_store(db),
    }


@router.get("/stores-by-country", response_model=List[StoreByCountryRead])
async def get_stores_by_country(db: AsyncSession = Depends(deps.get_db)):
    return await GeoManager.get_countries_and_active_stores(db)


@router.post("/stores/suggest")
async def suggest_new_store(
    suggested_store: SuggestedStore, db: AsyncSession = Depends(deps.get_db)
):
    db.add(suggested_store)
    await db.commit()
    return {"status": "ok"}


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
