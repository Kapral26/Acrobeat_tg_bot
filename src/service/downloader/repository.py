
"""
TODO попробовать достать музыку отсюда
https://ytmp3.cc
https://music.youtube.com


"""

import asyncio
from dataclasses import dataclass
from functools import partial

from yt_dlp import YoutubeDL


@dataclass
class DownloaderRepo:
    @staticmethod
    def _download(url: str, output_path: str):
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "quiet": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    async def download_track(self, url: str, output_path: str):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, partial(self._download, url, output_path))

    def _search_youtube(self, query: str, max_results: int = 3):
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
        results = await loop.run_in_executor(None, partial(self._search_youtube, query))

        return results
