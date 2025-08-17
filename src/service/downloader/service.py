import logging
from dataclasses import dataclass

from sqlalchemy.exc import NoResultFound

from src.domains.tracks.schemas import Track
from src.service.downloader.repository import DownloaderRepo
from src.service.settings.config import Settings


@dataclass
class DownloaderService:
    repository: DownloaderRepo
    settings: Settings
    logger: logging.Logger

    async def find_tracks_on_phrase(self, phrase: str) -> list[Track]:
        self.logger.debug(f"Searching for tracks on phrase '{phrase}'")
        results = await self.repository.find_tracks_on_phrase(phrase)
        if not results:
            raise NoResultFound
        self.logger.debug(f"Found {len(results)} tracks on phrase '{phrase}'")
        return [Track.model_validate(x) for x in results]

    async def download_track(self, url: str):
        self.logger.debug(f"Downloading track '{url}'")
        # todo удалить
        if not self.settings.path_audio.exists():
            self.settings.path_audio.mkdir()

        track_path = (self.settings.path_audio / "track").as_posix()
        self.logger.debug(f"Downloading track '{track_path}'")
        try:
            await self.repository.download_track(url, track_path)
        except Exception as e:
            self.logger.error(e)
            raise e
        else:
            return track_path
