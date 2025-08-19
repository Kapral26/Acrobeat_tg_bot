from pydantic import BaseModel, model_validator


class Track(BaseModel):
    title: str
    duration: int
    webpage_url: str
    minutes: int | None = None
    seconds: int | None = None

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def calculate_minutes_and_seconds(cls, values):
        duration = values.get("duration")
        if duration is not None:
            values["minutes"] = duration // 60
            values["seconds"] = duration % 60
        return values


class RepoTracks(BaseModel):
    tracks: list[Track]
    repo_alias: str


class DownloadTrackParams(BaseModel):
    repo_alias: str
    url: str

class DownloadYTParams(DownloadTrackParams):
    repo_alias: str = "yt"