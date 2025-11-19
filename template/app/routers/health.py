from fastapi import APIRouter
from app.dtos.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> HealthResponse:
    return HealthResponse()
