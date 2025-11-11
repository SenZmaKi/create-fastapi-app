from app.utils.settings import settings
from pydantic import BaseModel


class RootResponse(BaseModel):
    name: str = settings.app_name
    description: str = settings.app_description
    version: str = settings.app_version
    docs: str = "/docs"
    redoc: str = "/redoc"
