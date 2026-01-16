from datetime import timedelta
import datetime
from typing import Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import CursorResult, delete
from tenacity import retry, stop_after_attempt, wait_random_exponential
from app.database import AsyncSessionLocal
from app.models.utils.utils import Base, CanExpireMixin
from app.services.utils.utils import BaseService
from app.utils.logger import logger as parent_logger


logger = parent_logger.getChild("scheduler")


class SchedulerService(BaseService):
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_random_exponential(
            multiplier=2, min=timedelta(seconds=2), max=timedelta(minutes=5)
        ),
        before=lambda retry_state: logger.info(
            "Cleaning up expired data", extra={"attempt": retry_state.attempt_number}
        ),
        before_sleep=lambda retry_state: logger.info(
            "Failed to clean up expired data",
            extra={
                "attempt": retry_state.attempt_number,
                "exception": retry_state.outcome.exception(),  # pyright: ignore[reportOptionalMemberAccess]
            },
        ),
        retry_error_callback=lambda retry_state: logger.error(
            "Completely failed to clean up expired data",
            extra={
                "attempt": retry_state.attempt_number,
                "exception": retry_state.outcome.exception(),  # pyright: ignore[reportOptionalMemberAccess]
            },
        ),
    )
    async def cleanup_expired_data(self) -> None:
        async with AsyncSessionLocal() as db:
            total_deleted = 0
            # Iterate through models efficiently
            for mapper in Base.registry.mappers:
                model = mapper.class_

                # Type safety check for the mixin
                if (
                    model is None
                    or not isinstance(model, type)
                    or not issubclass(model, CanExpireMixin)
                ):
                    continue

                result: CursorResult = await db.execute(
                    delete(model).where(model.is_expired)
                )  # pyright: ignore[reportAssignmentType]
                total_deleted += result.rowcount

            await db.commit()
            logger.info(
                "Deleted expired records",
                extra={
                    "total_deleted": total_deleted,
                },
            )

    def start_scheduler(self) -> None:
        logger.info("Starting scheduler")
        if self.scheduler.running:
            logger.info("Scheduler already running")
            return
        self.scheduler.add_job(
            self.cleanup_expired_data,
            trigger=IntervalTrigger(days=1),
            id="cleanup_expired_data",
            name="Clean up expired data",
            replace_existing=True,
            next_run_time=datetime.datetime.now(),
        )

        self.scheduler.start()
        logger.info("Scheduler started")

    def shutdown_scheduler(self) -> None:
        if not self.scheduler.running:
            return
        self.scheduler.shutdown()
        logger.info("Scheduler shutdown successfully")


def create_get_scheduler_service() -> Callable[[], SchedulerService]:
    scheduler_service: SchedulerService | None = None

    def get_scheduler_service() -> SchedulerService:
        nonlocal scheduler_service
        if scheduler_service is None:
            scheduler_service = SchedulerService()
        return scheduler_service

    return get_scheduler_service


get_scheduler_service = create_get_scheduler_service()
