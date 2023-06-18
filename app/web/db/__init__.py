from sys import modules

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from web.core.config import settings

if "pytest" in modules:
    settings.DATABASE_URI += "_test"

engine = create_async_engine(settings.DATABASE_URI, echo=False, future=True)


async def get_async_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
