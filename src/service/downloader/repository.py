import asyncio
import logging
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from urllib.parse import quote, urljoin

import httpx
from aiogram import Bot
from bs4 import BeautifulSoup
from yt_dlp import DownloadError, YoutubeDL

from src.service.downloader.abstarction import DownloaderAbstractRepo
from src.service.downloader.cach_repository import DownloaderCacheRepo
from src.service.settings.config import Settings

logger = logging.getLogger(__name__)


@dataclass
class DownloaderRepoYT(DownloaderAbstractRepo):
    settings: Settings
    cache_repository: DownloaderCacheRepo
    priority: int = 11

    @property
    def alias(self) -> str:
        return "yt"

    def _download(self, url: str, output_path: Path):
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
            except DownloadError:  # noqa: TRY203
                raise

    async def download_track(self, bot: Bot, url: str, output_path: Path):
        loop = asyncio.get_event_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(None, self._download, url, output_path),
                timeout=30,
            )
        except asyncio.TimeoutError:  # noqa: UP041
            logger.exception("⏱️ Превышено время ожидания")
            return None
        except DownloadError as e:
            logger.exception(f"⚠️ Ошибка загрузки: {e}")
            return None

    def _search_track(self, query: str, max_results: int = 3):
        ydl_opts = {
            "quiet": True,
            "extract_flat": "in_playlist",  # не скачиваем, только метаданные
            "default_search": "ytsearch",
        }

        with YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch{max_results}:{query}"
            info = ydl.extract_info(search_query, download=False)
            return info["entries"]

    async def find_tracks_on_phrase(self, query: str, chat_id: int):
        loop = asyncio.get_event_loop()

        try:
            results = await asyncio.wait_for(
                loop.run_in_executor(None, partial(self._search_track, query)),
                timeout=30,
            )
        except asyncio.TimeoutError:  # noqa: UP041
            logger.exception("⏱️ Превышено время ожидания")
            return None
        except DownloadError as e:
            logger.exception(f"⚠️ Ошибка загрузки: {e}")
            return None

        if not results:
            return None

        for item in results:
            item["webpage_url"] = await self.cache_repository.set_track_url(
                item["url"], chat_id
            )

        return results


@dataclass
class DownloaderRepoPinkamuz(DownloaderAbstractRepo):
    settings: Settings
    cache_repository: DownloaderCacheRepo
    base_url: str = "https://pinkamuz.pro"
    priority: int = 10

    @property
    def alias(self) -> str:
        return "pin"

    @property
    def headers(self):
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
                    full_url, chat_id
                )
                results.append(
                    {
                        "title": title,
                        "webpage_url": url_cache_id,
                        "duration": duration,
                    }
                )

            return results

    async def find_tracks_on_phrase(self, query: str, chat_id: int) -> list[dict]:
        return await self._search_track(query=query, chat_id=chat_id)

    async def _download(self, url: str, output_path: Path) -> None:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(response.content)

    async def download_track(self, bot: Bot, url: str, output_path: Path) -> None:
        await self._download(url, output_path)


@dataclass
class TelegramDownloaderRepo(DownloaderAbstractRepo):
    priority = -100

    @property
    def alias(self) -> str:
        return "telegram"

    def _download(self, url: str, output_path: Path) -> None:
        pass

    def _search_track(self, query: str, max_results: int = 3) -> list[None]:
        return []

    async def find_tracks_on_phrase(self, query: str, chat_id: int) -> list[None]:
        return []

    async def download_track(self, bot: Bot, file_id: str, output_path: Path) -> None:
        try:
            file = await bot.get_file(file_id)
            await bot.download_file(file.file_path, destination=output_path)
        except Exception as e:
            raise RuntimeError(f"Ошибка при загрузке файла из Telegram: {e}")


@dataclass
class DownloaderRepoHitmo(DownloaderAbstractRepo):
    settings: Settings
    cache_repository: DownloaderCacheRepo
    base_url: str = "https://rus.hitmotop.com"
    priority: int = 5

    @property
    def alias(self) -> str:
        return "hitmo"

    @property
    def headers(self):
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
                    download_url, chat_id
                )

                results.append(
                    {
                        "title": f"{artist} - {title}",
                        "webpage_url": url_cache_id,
                        "duration": duration,
                    }
                )

            return results

    async def find_tracks_on_phrase(self, query: str, chat_id: int) -> list[dict]:
        return await self._search_track(query=query, chat_id=chat_id)

    async def _download(self, url: str, output_path: Path) -> None:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(response.content)

    async def download_track(self, bot: Bot, url: str, output_path: Path) -> None:
        await self._download(url, output_path)
