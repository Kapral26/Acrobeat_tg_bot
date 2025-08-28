import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from tempfile import gettempdir

from aiogram import Bot
from yt_dlp import DownloadError

from src.domains.tracks.schemas import DownloadTrackParams, RepoTracks, Track
from src.service.downloader.abstarction import DownloaderAbstractRepo
from src.service.downloader.cach_repository import DownloaderCacheRepo
from src.service.settings.config import Settings
from src.service.utils import processing_msg

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
        self, phrase: str, bot: Bot, chat_id: int, user_id: int
    ) -> RepoTracks | None:
        logger.debug(f"Searching for tracks on phrase '{phrase}'")

        self.external_repository.sort(key=lambda x: x.priority)
        for _idx, repo in enumerate(self.external_repository):
            logger.debug(f"Поиск в источнике {repo.alias}")
            try:
                founded_tracks = await processing_msg(
                    repo.find_tracks_on_phrase,
                    (phrase, chat_id),
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

        url_track = await self.cache_repository.get_track_url(
            download_params.url, chat_id=chat_id
        )

        try:
            await processing_msg(
                repo.download_track,
                (bot, url_track, track_path),
                bot=bot,
                chat_id=chat_id,
                spinner_msg="🛬 Загрузка трека на сервер",
            )
        except DownloadError:
            logger.exception("YouTrack не смог скачать аудио-дорожку")
            raise
        except Exception as error:
            logger.exception(error)  # noqa: TRY401
            raise
        else:
            return track_path


