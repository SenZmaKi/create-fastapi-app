from sqlalchemy import select
from app.services.utils.error import ServiceError
from app.services.utils.utils import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class UnhealthyDbError(ServiceError):
    pass


class HealthService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def check_health(self) -> UnhealthyDbError | None:
        try:
            await self.db.execute(select(1))
        except Exception as e:
            return UnhealthyDbError(f"Unhealthy database: {e}")
