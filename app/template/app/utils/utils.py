from datetime import UTC, datetime
from typing import Annotated
from pydantic import Field, GetCoreSchemaHandler
from pydantic_core import core_schema


class TZDatetimeCls(datetime):
    """Timezone-aware datetime class for Pydantic validation."""

    @classmethod
    def __get_pydantic_core_schema__(cls, _source, handler: GetCoreSchemaHandler):
        def validate_timezone_aware(dt: datetime) -> datetime:
            if dt.tzinfo is None:
                raise ValueError("Date must be timezone aware")
            return dt

        return core_schema.no_info_after_validator_function(
            validate_timezone_aware, handler(datetime)
        )


TZDatetime = Annotated[
    TZDatetimeCls,
    Field(
        description="Datetime in ISO format. Must include timezone information; UTC is recommended."
    ),
]


def utc_now() -> TZDatetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)  # pyright: ignore[reportReturnType]
