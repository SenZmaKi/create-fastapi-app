from fastapi import FastAPI
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIASGIMiddleware
from slowapi import Limiter
from app.utils.settings import settings

limiter = Limiter(key_func=get_remote_address, application_limits=[settings.rate_limit])


def add_rate_limiter_middleware(app: FastAPI) -> None:
    if settings.deployment_environment == "testing":
        return
    app.state.limiter = limiter
    app.add_middleware(SlowAPIASGIMiddleware)
