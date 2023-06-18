import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_app_metadata(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {'version', 'name', 'status'}
