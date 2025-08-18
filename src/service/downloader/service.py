import asyncio
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from tempfile import gettempdir
from typing import Any

from aiogram.types import Message

from src.domains.tracks.schemas import Track
from src.service.downloader.abstarction import DownloaderAbstractRepo
from src.service.settings.config import Settings


@dataclass
class DownloaderService:
    repository: list[DownloaderAbstractRepo]
    settings: Settings
    logger: logging.Logger

    async def find_tracks_on_phrase(
        self, phrase: str, message: Message
    ) -> list[Track] | None:
        self.logger.debug(f"Searching for tracks on phrase '{phrase}'")

        self.repository.sort(key=lambda x: x.priority)
        for _idx, repo in enumerate(self.repository):
            try:
                founded_tracks = await processing_msg(
                    repo.find_tracks_on_phrase,
                    (phrase,),
                    message=message,
                    spinner_msg=f"🔎Поиск в источнике {_idx + 1}/{len(self.repository)}",
                )
                if founded_tracks:
                    return [Track.model_validate(x) for x in founded_tracks]
            except Exception as e:
                print(f"Ошибка в {repo}: {e}")
                continue
        return None

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
