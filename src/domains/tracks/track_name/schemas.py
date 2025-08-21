from pydantic import BaseModel


class TrackNamePartSchema(BaseModel):
    id: int
    track_part: str

    class Config:
        from_attributes = True
