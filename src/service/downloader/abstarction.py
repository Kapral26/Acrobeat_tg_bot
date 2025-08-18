from abc import ABC, abstractmethod
from pathlib import Path


class DownloaderAbstractRepo(ABC):
    @abstractmethod
    def _download(self, url: str, output_path: Path) -> None:
        raise NotImplementedError

    @abstractmethod
    async def download_track(self, url: str, output_path: Path) -> None:
        raise NotImplementedError

    @abstractmethod
    def _search_track(self, query: str, max_results: int = 3) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    async def find_tracks_on_phrase(self, query: str) -> list[dict]:
        raise NotImplementedError
