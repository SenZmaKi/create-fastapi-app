from fastapi import APIRouter, Response, status
from app.dtos.health import HealthResponse
from app.services.health import UnhealthyDbError
from app.utils.dependencies import HealthServiceDependency

router = APIRouter(tags=["Health"])


@router.get("/health")
async def check_health(
    health_service: HealthServiceDependency, response: Response
) -> HealthResponse:
    result = await health_service.check_health()
    if isinstance(result, UnhealthyDbError):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return HealthResponse(status="unhealthy", message="Database is not healthy")
    return HealthResponse()
