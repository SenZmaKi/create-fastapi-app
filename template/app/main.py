from contextlib import asynccontextmanager
from typing import AsyncGenerator
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.utils.settings import settings
from app.utils.logger import logger
from app.routers import health, root
from app.database.session import close_db, init_db


def include_routers(app: FastAPI) -> None:
    app.include_router(root.router)
    app.include_router(health.router)
    # Include your routers here


def add_middlewares(app: FastAPI) -> None:
    add_cors_middleware(app)
    # Add your middlewares here


def add_cors_middleware(app: FastAPI) -> None:
    cors_kwargs = {
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
    if settings.env == "production":
        cors_kwargs["allow_origins"] = settings.cors_origins
    else:
        cors_kwargs["allow_origin_regex"] = ".*"

    app.add_middleware(
        CORSMiddleware,
        **cors_kwargs,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("🚀 Starting up...")
    logger.info("📊 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized!")

    yield

    # Shutdown
    logger.info("🛑 Shutting down...")
    await close_db()
    logger.info("✅ Database connections closed!")


def build_fastapi_app() -> FastAPI:
    return FastAPI(
        title=settings.app_name,
        debug=settings.fastapi_debug,
        version=settings.app_version,
        description=settings.app_description,
        lifespan=lifespan,
        docs_url="/docs",  # Swagger UI
        redoc_url="/redoc",  # ReDoc
        openapi_url="/openapi.json",
        openapi_tags=[
            {
                "name": "health",
                "description": "Health check endpoint",
            },
        ],
    )


async def generic_exception_handler(_: Request, exception: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception: {exception}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


def create_app() -> FastAPI:
    app = build_fastapi_app()
    include_routers(app)
    add_middlewares(app)
    app.add_exception_handler(Exception, generic_exception_handler)

    return app


app = create_app()


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.fastapi_reload,
        log_level=settings.fastapi_log_level,
        reload_includes=settings.fastapi_reload_includes,
    )


if __name__ == "__main__":
    main()
