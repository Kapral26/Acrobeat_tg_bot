"""
TODO попробовать достать музыку отсюда
https://ytmp3.cc
https://music.youtube.com


"""

import asyncio
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from urllib.parse import quote, urljoin

import httpx
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL

from src.service.downloader.abstarction import DownloaderAbstractRepo
from src.service.downloader.cach_repository import DownloaderCacheRepo
from src.service.settings.config import Settings


@dataclass
class DownloaderRepoYT(DownloaderAbstractRepo):
    settings: Settings
    cache_repository: DownloaderCacheRepo
    priority: int = 10

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
            "quiet": not self.settings.debug,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    async def download_track(self, url: str, output_path: Path):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, partial(self._download, url, output_path))

    def _search_track(self, query: str, max_results: int = 3):
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch{max_results}:{query}"
            info = ydl.extract_info(search_query, download=False)
            return info["entries"]

    async def find_tracks_on_phrase(self, query: str):
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, partial(self._search_track, query))
        async for item in results:
            item["webpage_url"] = await self.cache_repository.set_track_url(item["webpage_url"])

        return results


@dataclass
class DownloaderRepoPinkamuz(DownloaderAbstractRepo):
    settings: Settings
    cache_repository: DownloaderCacheRepo
    base_url: str = "https://pinkamuz.pro"
    priority: int = 0

    @property
    def alias(self) -> str:
        return "pin"

    @property
    def headers(self):
        return {
            "User-Agent": "Mozilla/5.0",
            "Referer": self.base_url,
        }

    async def _search_track(self, query: str, max_results: int = 3) -> list[dict]:
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
                url_cache_id = await self.cache_repository.set_track_url(full_url)
                results.append(
                    {
                        "title": title,
                        "webpage_url": url_cache_id,
                        "duration": duration,
                    }
                )

            return results

    async def find_tracks_on_phrase(self, query: str) -> list[dict]:
        return await self._search_track(query)

    async def _download(self, url: str, output_path: Path) -> None:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(response.content)

    async def download_track(self, url: str, output_path: Path) -> None:
        await self._download(url, output_path)
