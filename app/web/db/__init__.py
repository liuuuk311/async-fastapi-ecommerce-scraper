from web.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

engine = create_async_engine(settings.DATABASE_URI, echo=False, future=True)


async def get_async_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
