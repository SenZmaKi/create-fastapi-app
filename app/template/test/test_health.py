from httpx import AsyncClient
from test.utils.utils import assert_status_code
from test.utils.routes import HEALTH_URL


class TestHealthEndpoint:
    async def test_health_check(self, client: AsyncClient):
        response = await client.get(HEALTH_URL)
        await assert_status_code(response, 200)
        assert "status" in response.json()
