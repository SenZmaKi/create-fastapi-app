import os
import socket
from contextlib import closing
from collections.abc import AsyncGenerator
import pytest
import pytest_asyncio
from app.utils.settings import settings
from app.main import app
from httpx import ASGITransport, AsyncClient


os.environ["DEPLOYMENT_ENVIRONMENT"] = "testing"
SERVER_HOST = settings.fastapi_host
SERVER_PORT = settings.fastapi_port
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}/api/"


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


def is_port_in_use(port: int, host: str) -> bool:
    """Check if a port is in use."""

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        try:
            sock.settimeout(1)
            sock.connect((host, port))
            return True
        except (TimeoutError, OSError):
            return False


@pytest.fixture(scope="session")
def transport() -> ASGITransport:
    return ASGITransport(app)


@pytest_asyncio.fixture(scope="function")
async def client(
    base_url: str,
    transport: ASGITransport,
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=transport, base_url=base_url, timeout=30.0) as ac:
        yield ac
