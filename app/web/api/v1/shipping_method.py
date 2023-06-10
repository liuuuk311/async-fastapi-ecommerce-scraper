import logging
from typing import List

from web.api import deps
from fastapi import APIRouter, Depends
from web.models.shipping import ShippingMethod, ShippingMethodRead
from web.models.store import Store
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get(
    "/shipping_methods/{store_public_id}", response_model=List[ShippingMethodRead]
)
async def get_shipping_method(
    store_public_id,
    db: AsyncSession = Depends(deps.get_db),
):
    stmt = (
        select(ShippingMethod)
        .join(Store)
        .where(
            Store.public_id == store_public_id,
            Store.is_active.is_(True),
            ShippingMethod.is_active.is_(True),
        )
        .order_by(ShippingMethod.price)
    )

    return (await db.execute(stmt)).scalars()
