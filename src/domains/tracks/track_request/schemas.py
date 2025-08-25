from pydantic import BaseModel


class TrackRequestSchema(BaseModel):
    user_id: int
    query_text: str

