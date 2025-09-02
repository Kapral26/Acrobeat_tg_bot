"""
Модуль `abstraction.py` определяет абстрактный интерфейс для репозиториев, отвечающих за поиск и загрузку музыкальных треков.

Этот интерфейс используется для унификации работы с разными источниками (YouTube, Pinkamuz, Telegram и др.), обеспечивая единое API
для поиска и загрузки треков вне зависимости от их источника.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from aiogram import Bot


class DownloaderAbstractRepo(ABC):
    """
    Абстрактный класс-интерфейс для всех репозиториев, связанных с загрузкой и поиском музыкальных треков.

    Каждый конкретный репозиторий должен реализовать все абстрактные методы этого класса.
    """

    @property
    @abstractmethod
    def alias(self) -> str:
        """Возвращает уникальный алиас репозитория (например, 'yt' для YouTube)."""
        raise NotImplementedError

    @abstractmethod
    def _download(self, url: str, output_path: Path) -> None:
        """
        Синхронный метод для загрузки аудиофайла из указанного URL.

        :param url: URL файла для загрузки.
        :param output_path: Путь к выходному файлу.
        """
        raise NotImplementedError

    @abstractmethod
    async def download_track(self, bot: Bot, url: str, output_path: Path) -> None:
        """
        Асинхронная обёртка над `_download`, используемая в основном коде приложения.

        :param bot: Экземпляр бота Aiogram.
        :param url: URL файла для загрузки.
        :param output_path: Путь к выходному файлу.
        """
        raise NotImplementedError

    @abstractmethod
    def _search_track(
        self, query: str, chat_id: int, max_results: int = 3
    ) -> list[dict]:
        """
        Синхронный метод для поиска треков по ключевой фразе.

        :param query: Ключевая фраза для поиска.
        :param chat_id: ID чата, используется для кэширования ссылок.
        :param max_results: Максимальное количество результатов.
        :return: Список найденных треков в виде словарей.
        """
        raise NotImplementedError

    @abstractmethod
    async def find_tracks_on_phrase(self, query: str, chat_id: int) -> list[dict]:
        """
        Асинхронная обёртка над `_search_track`.

        :param query: Ключевая фраза для поиска.
        :param chat_id: ID чата, используется для кэширования ссылок.
        :return: Список найденных треков.
        """
        raise NotImplementedError
