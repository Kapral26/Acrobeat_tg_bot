from pydantic import BaseModel, computed_field


class Track(BaseModel):
    title: str
    duration: int
    webpage_url: str

    class Config:
        from_attributes = True

    @computed_field
    @property
    def minutes(self) -> int:
        return self.duration // 60

    @computed_field
    @property
    def seconds(self) -> int:
        return self.duration % 60


class RepoTracks(BaseModel):
    tracks: list[Track]
    repo_alias: str


class DownloadTrackParams(BaseModel):
    repo_alias: str
    url: str


class DownloadYTParams(DownloadTrackParams):
    repo_alias: str = "yt"


class DownloadTelegramParams(DownloadTrackParams):
    repo_alias: str = "telegram"
    url: int
