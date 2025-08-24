from collections.abc import Sequence
from dataclasses import dataclass

from src.domains.tracks.track_storage.models import DownloadedTrack
from src.domains.tracks.track_storage.repository import TrackStorageRepository
from src.domains.tracks.track_storage.schemas import TrackCreateSchema


@dataclass
class TrackStorageService:
    repository: TrackStorageRepository

    async def create_downloaded_track(self, track_data: TrackCreateSchema) -> None:
        await self.repository.insert_downloaded_track(track_data)

    async def delete_downloaded_track(self, track_id: int) -> bool:
        return await self.repository.delete_downloaded_track(track_id)

    async def get_downloaded_track_by_id(self, track_id: int) -> DownloadedTrack | None:
        return await self.repository.get_downloaded_track_by_id(track_id)

    async def get_downloaded_track_by_source_url(
        self, source_url: str
    ) -> DownloadedTrack | None:
        return await self.repository.get_downloaded_track_by_source_url(source_url)

    async def get_downloaded_tracks_by_title(
        self, title: str
    ) -> Sequence[DownloadedTrack]:
        return await self.repository.get_downloaded_tracks_by_title(title)

    async def get_downloaded_tracks_by_artist(
        self, artist: str
    ) -> Sequence[DownloadedTrack]:
        return await self.repository.get_downloaded_tracks_by_artist(artist)

    async def search_downloaded_tracks(
        self, track_data: TrackCreateSchema
    ) -> DownloadedTrack | None:
        return await self.repository.search_downloaded_tracks(track_data)
