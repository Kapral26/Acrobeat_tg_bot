from dataclasses import dataclass

from sqlalchemy.exc import NoResultFound

from src.domains.tracks.schemas import Track
from src.service.downloader.repository import DownloaderRepo


@dataclass
class DownloaderService:
    repository: DownloaderRepo

    async def find_tracks_on_phrase(self, phrase: str) -> list[Track]:
        results = await self.repository.find_tracks_on_phrase(phrase)
        if not results:
            raise NoResultFound

        return [Track.model_validate(x) for x in results]
