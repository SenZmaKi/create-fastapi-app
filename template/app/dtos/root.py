from typing import Self
from fastapi import Request
from app.utils.settings import settings
from pydantic import BaseModel


class RootResponse(BaseModel):
    name: str = settings.app_name
    description: str = settings.app_description
    version: str = settings.app_version
    docs: str
    redoc: str

    @classmethod
    def from_request(cls, request: Request) -> Self:
        base = str(request.base_url).rstrip("/")
        return cls(docs=f"{base}/docs", redoc=f"{base}/redoc")
