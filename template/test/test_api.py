from collections.abc import AsyncGenerator
import aiohttp
import pytest
import pytest_asyncio
from aiohttp import ClientSession, CookieJar


@pytest_asyncio.fixture(scope="function")
async def client(
    base_url: str, verify_server: None
) -> AsyncGenerator[ClientSession, None]:
    jar = CookieJar()
    async with ClientSession(
        base_url=base_url, timeout=aiohttp.ClientTimeout(total=30.0), cookie_jar=jar
    ) as ac:
        yield ac


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_check(self, client: ClientSession):
        response = await client.get("/health")
        assert response.status == 200
        assert "status" in await response.json()
