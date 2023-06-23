import asyncio
from typing import Generator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from web.core.config import settings
from web.main import app
from .fixtures import *

from sqlmodel.ext.asyncio.session import AsyncSession

from web.api.deps import get_db


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncSession:
    engine = create_async_engine(
        settings.DATABASE_URI,
        echo=False,
        future=True,
    )
    session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as s:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        yield s

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


app.dependency_overrides[get_db] = db


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url=f"http://") as c:
        yield c


@pytest_asyncio.fixture
async def api_client():
    async with AsyncClient(app=app, base_url=f"http://{settings.API_PREFIX}") as c:
        yield c
