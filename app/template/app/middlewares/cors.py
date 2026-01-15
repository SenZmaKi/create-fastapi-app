from fastapi.middleware.cors import CORSMiddleware
from app.utils.settings import settings
from fastapi import FastAPI


def add_cors_middleware(app: FastAPI) -> None:
    cors_kwargs = {
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
        "expose_headers": ["*"],
    }
    if settings.deployment_environment == "production":
        cors_kwargs["allow_origins"] = settings.cors_origins
    else:
        cors_kwargs["allow_origin_regex"] = ".*"

    app.add_middleware(
        CORSMiddleware,
        **cors_kwargs,
    )
