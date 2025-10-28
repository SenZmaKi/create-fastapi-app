from fastapi import APIRouter
from app.utils.settings import settings

router = APIRouter(tags=["root"])


@router.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "description": settings.app_description,
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
    }
