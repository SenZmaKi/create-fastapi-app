from pydantic import BaseModel, StringConstraints
from typing import Annotated


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


DBStr = Annotated[str, StringConstraints(min_length=1, max_length=255)]
IDStr = Annotated[str, StringConstraints(min_length=1, max_length=36)]
NotesStr = Annotated[str, StringConstraints(max_length=1000)]
