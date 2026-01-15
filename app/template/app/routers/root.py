from fastapi import APIRouter, Request
from app.dtos.root import RootResponse


router = APIRouter(prefix="", tags=["Root"])


@router.get("/")
async def root(
    request: Request,
) -> RootResponse:
    return RootResponse.from_request(request=request)
