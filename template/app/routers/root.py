from fastapi import APIRouter
from template.app.dtos.root import RootResponse

router = APIRouter(tags=["Root"])


@router.get("/")
async def root() -> RootResponse:
    return RootResponse()
