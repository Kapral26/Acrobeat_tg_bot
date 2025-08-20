from pydantic import BaseModel


class TrackPartSchema(BaseModel):
    id: int
    track_part: str

    class Config:
        from_attributes = True
