from datetime import datetime

from pydantic import BaseModel


class TrackCreateSchema(BaseModel):
    title: str
    artist: str | None = None
    duration: int | None = None
    source_url: str
    platform: str | None = None


class TrackResponseSchema(TrackCreateSchema):
    id: int


class TrackFullSchema(TrackResponseSchema):
    expires_at: datetime
    # Можно добавить поле clips, если нужно
    # clips: list["ClipSchema"] = []
