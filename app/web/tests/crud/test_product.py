from _decimal import Decimal
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from web.crud.product import crud_product
from web.models.import_query import ImportQuery
from web.models.product import Product
from web.models.schemas import ProductCreate
from web.models.store import Store
from web.tests.utils.text import random_lower_string


@pytest.mark.asyncio
async def test_merge_product(db: AsyncSession, store: Store, import_query: ImportQuery):
    obj_in = ProductCreate(
        id="unique_id",
        store_id=store.id,
        import_query_id=import_query.id,
        description=random_lower_string(),
        import_date=datetime.utcnow(),
        is_active=True,
        name=random_lower_string(),
        price=Decimal("10"),
        currency=store.currency,
        link=random_lower_string(),
    )
    # First create
    await crud_product.merge(db, obj_in=obj_in)
    db_obj: Product = (await db.execute(select(Product))).scalars().first()

    assert db_obj.price == obj_in.price == Decimal("10")
    assert db_obj.id == obj_in.id == "unique_id"

    # Then update with a new price
    obj_in.price = Decimal("100")
    await crud_product.merge(db, obj_in=obj_in)
    assert db_obj.price == obj_in.price == Decimal("100")
    assert db_obj.id == obj_in.id == "unique_id"
