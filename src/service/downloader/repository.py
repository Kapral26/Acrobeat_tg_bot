"""
Модуль `repository.py` содержит реализацию репозиториев
 для поиска и загрузки музыкальных треков.

Реализованы следующие репозитории:
- `DownloaderRepoYT`: Поиск и загрузка с YouTube.
- `DownloaderRepoPinkamuz`: Поиск и загрузка с сайта Pinkamuz.
- `TelegramDownloaderRepo`: Загрузка файлов из Telegram.
- `DownloaderRepoHitmo`: Поиск и загрузка с сайта Hitmotop.

Каждый репозиторий реализует интерфейс `DownloaderAbstractRepo`,
 предоставляя методы `find_tracks_on_phrase` и `download_track`.
"""

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, urljoin

import aiofiles
import httpx
from aiogram import Bot
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError  # Исправленный импорт исключения

from src.service.downloader.abstraction import DownloaderAbstractRepo
from src.service.downloader.cache_repository import DownloaderCacheRepo
from src.service.settings.config import Settings

logger = logging.getLogger(__name__)


@dataclass
class DownloaderRepoYT(DownloaderAbstractRepo):
    """
    Репозиторий для поиска и загрузки музыки с YouTube.

    Использует библиотеку `yt-dlp` для извлечения метаданных и загрузки аудио.
    """

    settings: Settings
    cache_repository: DownloaderCacheRepo
    priority: int = 11

    @property
    def alias(self) -> str:
        """Алиас репозитория."""
        return "yt"

    def _download(self, url: str, output_path: Path) -> None:
        """
        Синхронная загрузка аудиофайла с YouTube.

        :param url: URL видео на YouTube.
        :param output_path: Путь к выходному файлу (без расширения).
        :raises DownloadError: Если произошла ошибка загрузки.
        """
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path.with_suffix("").as_posix(),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
            ],
            "extractor_args": {
                "youtube": ["formats=missing_pot"],
            },
            "quiet": not self.settings.debug,
            "verbose": True,
            "socket_timeout": 15,
            "retries": 3,
        }

        with YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except DownloadError:
                logger.exception("YT Download failed")
                raise

    async def download_track(self, bot: Bot, url: str, output_path: Path) -> None:  # noqa: ARG002
        """
        Асинхронная загрузка трека с YouTube.

        :param bot: Экземпляр бота Aiogram.
        :param url: URL трека.
        :param output_path: Путь к выходному файлу.
        :return: `None` при успешной загрузке, или `None` при ошибке.
        """
        loop = asyncio.get_event_loop()
        try:
            await asyncio.wait_for(
                loop.run_in_executor(None, self._download, url, output_path),
                timeout=30,
            )
        except asyncio.TimeoutError:  # noqa: UP041
            logger.exception("⏱️ Превышено время ожидания")
        except DownloadError:
            logger.exception("⚠️ Ошибка загрузки")

    def _search_track(
        self,
        query: str,
        chat_id: int = 0,  # noqa: ARG002
        max_results: int = 3,
    ) -> list[dict]:
        """
        Поиск треков на YouTube по ключевой фразе.

        :param query: Ключевая фраза для поиска.
        :param max_results: Максимальное количество результатов.
        :return: Список найденных треков в виде словарей.
        """
        ydl_opts = {
            "quiet": True,
            "extract_flat": "in_playlist",  # не скачиваем, только метаданные
            "default_search": "ytsearch",
        }

        with YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch{max_results}:{query}"
            info = ydl.extract_info(search_query, download=False)
            return info["entries"]

    async def find_tracks_on_phrase(
        self,
        query: str,
        chat_id: int,
    ) -> list[dict] | None:
        """
        Асинхронный поиск треков по ключевой фразе.

        :param query: Ключевая фраза для поиска.
        :param chat_id: ID чата для кэширования ссылки.
        :return: Список найденных треков или `None` при ошибке.
        """
        loop = asyncio.get_event_loop()

        try:
            results = await asyncio.wait_for(
                loop.run_in_executor(None, self._search_track, query, chat_id, 3),
                timeout=30,
            )
        except TimeoutError:
            logger.exception("⏱️ Превышено время ожидания")
            return None
        except DownloadError:
            logger.exception("⚠️ Ошибка загрузки")
            return None

        if not results:
            return None

        for item in results:
            item["webpage_url"] = await self.cache_repository.set_track_url(
                item["url"],
                chat_id,
            )

        return results


@dataclass
class DownloaderRepoPinkamuz(DownloaderAbstractRepo):
    """
    Репозиторий для поиска и загрузки музыки с сайта Pinkamuz.

    Использует HTTP-запросы и парсинг HTML-страницы для получения информации о треках.
    """

    settings: Settings
    cache_repository: DownloaderCacheRepo
    base_url: str = "https://pinkamuz.pro"
    priority: int = 10

    @property
    def alias(self) -> str:
        """Алиас репозитория."""
        return "pin"

    @property
    def headers(self) -> dict:
        """HTTP-заголовки для запросов."""
        return {
            "User-Agent": "Mozilla/5.0",
            "Referer": self.base_url,
        }

    async def _search_track(
        self,
        query: str,
        chat_id: int,
        max_results: int = 3,
    ) -> list[dict]:
        """
        Поиск треков на сайте Pinkamuz по ключевой фразе.

        :param query: Ключевая фраза для поиска.
        :param chat_id: ID чата для кэширования ссылки.
        :param max_results: Максимальное количество результатов.
        :return: Список найденных треков в виде словарей.
        """
        search_url = f"{self.base_url}/search/{quote(query)}"

        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            response = await client.get(search_url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            track_blocks = soup.select("div.track")[:max_results]

            results = []
            for block in track_blocks:
                # Название и артист
                name_block = block.select_one("div.name-text")
                if not name_block:
                    continue

                artist_tag = name_block.select_one("span.artist")
                title_tag = name_block.select_one("span.title")
                if not artist_tag or not title_tag:
                    continue

                title = f"{artist_tag.get_text(strip=True)} - {title_tag.get_text(strip=True)}"

                # Длительность
                time_tag = block.select_one("div.name-time")
                if not time_tag:
                    continue

                try:
                    mins, secs = map(int, time_tag.get_text(strip=True).split(":"))
                    duration = mins * 60 + secs
                except ValueError:
                    continue

                # Ссылка на mp3
                download_tag = block.select_one("a.link[href*='/download/']")
                if not download_tag:
                    continue

                href = download_tag.get("href")
                full_url = urljoin("https://track.pinkamuz.pro", href)
                url_cache_id = await self.cache_repository.set_track_url(
                    full_url,
                    chat_id,
                )
                results.append(
                    {
                        "title": title,
                        "webpage_url": url_cache_id,
                        "duration": duration,
                    },
                )

            return results

    async def find_tracks_on_phrase(self, query: str, chat_id: int) -> list[dict]:
        """
        Асинхронный поиск треков на сайте Pinkamuz.

        :param query: Ключевая фраза для поиска.
        :param chat_id: ID чата для кэширования ссылки.
        :return: Список найденных треков.
        """
        return await self._search_track(query=query, chat_id=chat_id)

    async def _download(self, url: str, output_path: Path) -> None:
        """
        Скачивание аудиофайла с сайта Pinkamuz.

        :param url: URL файла для загрузки.
        :param output_path: Путь к выходному файлу.
        """
        async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()

            async with aiofiles.open(output_path, mode="wb") as f:
                await f.write(response.content)

    async def download_track(self, bot: Bot, url: str, output_path: Path) -> None:  # noqa: ARG002
        """
        Асинхронная загрузка трека.

        :param bot: Экземпляр бота Aiogram.
        :param url: URL трека.
        :param output_path: Путь к выходному файлу.
        """
        await self._download(url, output_path)


@dataclass
class TelegramDownloaderRepo(DownloaderAbstractRepo):
    """
    Репозиторий для загрузки файлов из Telegram.

    Поддерживает загрузку медиафайлов, отправленных пользователем.
    """

    priority = -100

    @property
    def alias(self) -> str:
        """Алиас репозитория."""
        return "telegram"

    def _download(self, url: str, output_path: Path) -> None:
        """Заглушка — не используется."""

    def _search_track(
        self,
        query: str,  # noqa: ARG002
        chat_id: int = 0,  # noqa: ARG002
        max_results: int = 3,  # noqa: ARG002
    ) -> list[None]:
        """Заглушка — не используется."""
        return []

    async def find_tracks_on_phrase(self, query: str, chat_id: int) -> list[None]:  # noqa: ARG002
        """Заглушка — не используется."""
        return []

    async def download_track(self, bot: Bot, file_id: str, output_path: Path) -> None:
        """
        Загрузка файла из Telegram.

        :param bot: Экземпляр бота Aiogram.
        :param file_id: ID файла.
        :param output_path: Путь к выходному файлу.
        :raises RuntimeError: При ошибке загрузки.
        """
        try:
            file = await bot.get_file(file_id)
            await bot.download_file(file.file_path, destination=output_path)
        except Exception as e:  # noqa: BLE001
            msg = f"Ошибка при загрузке файла из Telegram: {e}"
            raise RuntimeError(msg)


@dataclass
class DownloaderRepoHitmo(DownloaderAbstractRepo):
    """
    Репозиторий для поиска и загрузки музыки с сайта Hitmotop.

    Использует HTTP-запросы и парсинг HTML-страницы для получения информации о треках.
    """

    settings: Settings
    cache_repository: DownloaderCacheRepo
    base_url: str = "https://rus.hitmotop.com"
    priority: int = 5

    @property
    def alias(self) -> str:
        """Алиас репозитория."""
        return "hitmo"

    @property
    def headers(self) -> dict:
        """HTTP-заголовки для запросов."""
        return {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/136.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
            "Referer": self.base_url,
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def _search_track(
        self,
        query: str,
        chat_id: int,
        max_results: int = 3,
    ) -> list[dict]:
        """
        Поиск треков на сайте Hitmotop по ключевой фразе.

        :param query: Ключевая фраза для поиска.
        :param chat_id: ID чата для кэширования ссылки.
        :param max_results: Максимальное количество результатов.
        :return: Список найденных треков в виде словарей.
        """
        search_url = f"{self.base_url}/search?q={quote(query)}"

        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            response = await client.get(search_url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            tracks = soup.select("li.tracks__item")[:max_results]

            results = []
            for track in tracks:
                title_tag = track.select_one("div.track__title")
                artist_tag = track.select_one("div.track__desc")
                length_tag = track.select_one("div.track__fulltime")
                download_tag = track.select_one("a.track__download-btn")

                if not (title_tag and artist_tag and length_tag and download_tag):
                    continue

                title = title_tag.get_text(strip=True)
                artist = artist_tag.get_text(strip=True)
                length_str = length_tag.get_text(strip=True)

                # конвертируем длительность в секунды
                try:
                    mins, secs = map(int, length_str.split(":"))
                    duration = mins * 60 + secs
                except ValueError:
                    duration = 0

                download_url = urljoin(self.base_url, download_tag["href"])
                url_cache_id = await self.cache_repository.set_track_url(
                    download_url,
                    chat_id,
                )

                results.append(
                    {
                        "title": f"{artist} - {title}",
                        "webpage_url": url_cache_id,
                        "duration": duration,
                    },
                )

            return results

    async def find_tracks_on_phrase(self, query: str, chat_id: int) -> list[dict]:
        """
        Асинхронный поиск треков на сайте Hitmotop.

        :param query: Ключевая фраза для поиска.
        :param chat_id: ID чата для кэширования ссылки.
        :return: Список найденных треков.
        """
        return await self._search_track(query=query, chat_id=chat_id)

    async def _download(self, url: str, output_path: Path) -> None:
        """
        Скачивание аудиофайла с сайта Hitmotop.

        :param url: URL файла для загрузки.
        :param output_path: Путь к выходному файлу.
        """
        async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()

            async with aiofiles.open(output_path, "wb") as f:
                await f.write(response.content)

    async def download_track(self, bot: Bot, url: str, output_path: Path) -> None:  # noqa: ARG002
        """
        Асинхронная загрузка трека.

        :param bot: Экземпляр бота Aiogram.
        :param url: URL трека.
        :param output_path: Путь к выходному файлу.
        """
        await self._download(url, output_path)
