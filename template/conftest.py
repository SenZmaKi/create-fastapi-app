import os
import socket
import subprocess
from collections.abc import Generator
from contextlib import closing
from typing import NoReturn

import pytest
from tenacity import retry, retry_if_result, stop_after_delay, wait_fixed


from app.utils.settings import settings


SERVER_HOST = settings.fastapi_host
SERVER_PORT = settings.fastapi_port
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"


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
def verify_server() -> Generator[None | NoReturn, None, None]:
    """Start the server if it's not already running.

    This fixture ensures the server is available for testing and properly
    handles cleanup. It avoids event loop issues by running the server
    in a separate process.
    """

    # Check if server is already running
    if is_port_in_use(SERVER_PORT, SERVER_HOST):
        print(f"\n✅ Server already running on {SERVER_HOST}:{SERVER_PORT}")
        yield None
        return

    # Start the server in a subprocess
    print(f"\n🚀 Starting server on {SERVER_HOST}:{SERVER_PORT}...")
    env = os.environ.copy()
    env["ENV"] = "testing"
    process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", SERVER_HOST, "--port", str(SERVER_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    # Wait for the server to start using tenacity
    @retry(
        stop=stop_after_delay(10),
        wait=wait_fixed(0.5),
        retry=retry_if_result(lambda x: not x),
    )
    def wait_for_server() -> bool:
        if process.poll() is not None:
            # Process has terminated
            stdout, stderr = process.communicate()
            print("❌ Server failed to start!")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            pytest.exit("Server failed to start", returncode=1)
        return is_port_in_use(SERVER_PORT, SERVER_HOST)

    def cleanup_and_exit(exit_reason: str):
        process.terminate()
        process.wait(timeout=5)
        pytest.exit(exit_reason, returncode=1)

    try:
        if wait_for_server():
            print("✅ Server started successfully!")
        else:
            cleanup_and_exit("Server did not start within 10 seconds")
    except Exception as e:
        cleanup_and_exit(f"Server failed to start: {e}")

    yield

    # Cleanup: stop the server
    print("\n🛑 Stopping test server...")
    process.terminate()
    try:
        process.wait(timeout=5)
        print("✅ Server stopped gracefully")
    except subprocess.TimeoutExpired:
        print("⚠️  Server did not stop gracefully, forcing...")
        process.kill()
        process.wait()
        print("✅ Server stopped forcefully")
