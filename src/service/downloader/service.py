import asyncio
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from tempfile import gettempdir
from typing import Any

from aiogram import Bot

from src.domains.tracks.schemas import DownloadTrackParams, RepoTracks, Track
from src.service.downloader.abstarction import DownloaderAbstractRepo
from src.service.downloader.cach_repository import DownloaderCacheRepo
from src.service.settings.config import Settings

logger = logging.getLogger(__name__)


@dataclass
class DownloaderService:
    external_repository: list[DownloaderAbstractRepo]
    cache_repository: DownloaderCacheRepo
    settings: Settings

    def _get_repo(self, repo_alias: str) -> DownloaderAbstractRepo:
        repo = next(x for x in self.external_repository if x.alias == repo_alias)
        return repo

    async def find_tracks_on_phrase(
        self,
        phrase: str,
        bot: Bot,
        chat_id: int,
    ) -> RepoTracks | None:
        logger.debug(f"Searching for tracks on phrase '{phrase}'")

        self.external_repository.sort(key=lambda x: x.priority)
        for _idx, repo in enumerate(self.external_repository):
            logger.debug(f"Поиск в источнике {repo.alias}")
            try:
                founded_tracks = await processing_msg(
                    repo.find_tracks_on_phrase,
                    (phrase,),
                    bot=bot,
                    chat_id=chat_id,
                    spinner_msg=f"🔎Поиск в источнике {_idx + 1}/{len(self.external_repository)}",
                )
                if founded_tracks:
                    return RepoTracks(
                        tracks=[Track.model_validate(x) for x in founded_tracks],
                        repo_alias=repo.alias,
                    )
            except Exception as e:
                logger.exception(f"Ошибка в {repo.alias}: {e}")
                continue
        return None

    async def download_track(
        self, download_params: DownloadTrackParams, bot: Bot, chat_id: int
    ):
        logger.debug(
            f"Downloading track '{download_params.url}', repo: '{download_params.repo_alias}'"
        )
        track_path = Path(gettempdir()) / f"{uuid.uuid4()}.mp3"

        repo = self._get_repo(download_params.repo_alias)

        url_track = await self.cache_repository.get_track_url(download_params.url)

        try:
            await processing_msg(
                repo.download_track,
                (bot, url_track, track_path),
                bot=bot,
                chat_id=chat_id,
                spinner_msg="🛬 Загрузка трека на сервер",
            )
        except Exception as error:
            logger.exception(error)  # noqa: TRY401
            raise
        else:
            return track_path

    # async def download_track_from_tg(
    #         self,
    #         bot: Bot,
    #         chat_id: int,
    #         file_id: str,
    # ):
    #     track_path = Path(gettempdir()) / f"{uuid.uuid4()}.mp3"
    #
    #     try:
    #         await processing_msg(
    #             self.repository_telegram.download_track,
    #             (bot, file_id, track_path),
    #             bot=bot,
    #             chat_id=chat_id,
    #             spinner_msg="🛬 Загрузка трека на сервер",
    #         )
    #     except Exception as error:
    #         logger.exception(error)
    #         raise
    #     else:
    #         return track_path


async def processing_msg(
    func: callable, args: tuple, bot: Bot, chat_id: int, spinner_msg: str
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
    loading_msg = await bot.send_message(chat_id=chat_id, text=spinner[index])
    task = asyncio.create_task(func(*args))
    while not task.done():
        index = (index + 1) % len(spinner)
        await loading_msg.edit_text(spinner[index])
        await asyncio.sleep(0.2)
    task_result = task.result()
    await loading_msg.delete()
    return task_result
