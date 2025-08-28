from abc import ABC, abstractmethod
from pathlib import Path

from aiogram import Bot


class DownloaderAbstractRepo(ABC):
    @property
    @abstractmethod
    def alias(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _download(self, url: str, output_path: Path) -> None:
        raise NotImplementedError

    @abstractmethod
    async def download_track(self, bot: Bot, url: str, output_path: Path) -> None:
        raise NotImplementedError

    @abstractmethod
    def _search_track(
        self, query: str, chat_id: int, max_results: int = 3
    ) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    async def find_tracks_on_phrase(self, query: str, chat_id: int) -> list[dict]:
        raise NotImplementedError
