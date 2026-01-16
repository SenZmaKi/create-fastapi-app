from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "healthy"
    message: str | None = None
