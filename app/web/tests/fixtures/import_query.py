import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession

from web.models.import_query import ImportQuery
from web.tests.utils.text import random_lower_string


@pytest_asyncio.fixture
async def import_query(db: AsyncSession):
    iq = ImportQuery(text=random_lower_string())
    db.add(iq)
    await db.commit()
    return iq
