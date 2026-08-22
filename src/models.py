from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel

accepted_keys = ["original_url", "short_name"]


class Link(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    original_url: str
    short_name: str
    short_url: str
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
