import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession

from web.models.store import Store
from web.tests.utils.text import random_lower_string


@pytest_asyncio.fixture
async def store(db: AsyncSession):
    s = Store(
        name=random_lower_string(),
        currency="EUR",
        website=random_lower_string(),
        search_url=random_lower_string(),
        search_tag=random_lower_string(),
        search_class=random_lower_string(),
        search_link=random_lower_string(),
        product_name_class=random_lower_string(),
        product_name_tag=random_lower_string(),
        product_price_class=random_lower_string(),
        product_price_tag=random_lower_string(),
    )
    db.add(s)
    await db.commit()
    return s
