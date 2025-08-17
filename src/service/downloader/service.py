import asyncio
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from tempfile import gettempdir
from typing import Any

from aiogram.types import Message
from sqlalchemy.exc import NoResultFound

from src.domains.tracks.schemas import Track
from src.service.downloader.repository import DownloaderRepo
from src.service.settings.config import Settings


@dataclass
class DownloaderService:
    repository: DownloaderRepo
    settings: Settings
    logger: logging.Logger

    async def find_tracks_on_phrase(self, phrase: str, message: Message) -> list[Track]:
        self.logger.debug(f"Searching for tracks on phrase '{phrase}'")

        founded_tracks = await processing_msg(
            self.repository.find_tracks_on_phrase,
            (phrase,),
            message=message,
            spinner_msg="🔎Поиск",
        )

        if not founded_tracks:
            raise NoResultFound

        return [Track.model_validate(x) for x in founded_tracks]

    async def download_track(self, url: str, message: Message):
        self.logger.debug(f"Downloading track '{url}'")
        track_path = Path(gettempdir()) / f"{uuid.uuid4()}.mp3"

        await processing_msg(
            self.repository.download_track,
            (url, track_path),
            message=message,
            spinner_msg="🛬 Загрузка трека на сервер",
        )

        return track_path


async def processing_msg(
    func: callable, args: tuple, message: Message, spinner_msg: str
) -> Any:  # noqa: ANN401
    """Метод для отрисовки анимации выполнения действия."""
    spinner = [
        f"{spinner_msg} ⠋",
        f"{spinner_msg} ⠙",
        f"{spinner_msg} ⠹",
        f"{spinner_msg} ⠸",
        f"{spinner_msg} ⠼",
        f"{spinner_msg} ⠴",
        f"{spinner_msg} ⠦",
        f"{spinner_msg} ⠧",
        f"{spinner_msg} ⠇",
        f"{spinner_msg} ⠏",
    ]
    index = 0
    loading_msg = await message.answer(spinner[index])
    task = asyncio.create_task(func(*args))
    # Анимация спиннера до завершения задачи
    while not task.done():
        index = (index + 1) % len(spinner)
        await loading_msg.edit_text(spinner[index])
        await asyncio.sleep(0.2)
    task_result = task.result()
    await loading_msg.delete()
    return task_result
