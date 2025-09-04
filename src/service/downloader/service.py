"""
Модуль `service.py` содержит реализацию сервиса для поиска и загрузки музыкальных треков.

Сервис использует репозитории, реализующие интерфейс `DownloaderAbstractRepo`, для выполнения
поиска треков по ключевым фразам и их загрузки. Также используется кэширующий репозиторий,
который позволяет избегать повторного обработки уже загруженных треков.
"""

import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from tempfile import gettempdir

from aiogram import Bot
from yt_dlp.utils import DownloadError

from src.domains.common.message_processing import processing_msg
from src.domains.tracks.schemas import DownloadTrackParams, RepoTracks, Track
from src.service.downloader.abstraction import DownloaderAbstractRepo
from src.service.downloader.cache_repository import DownloaderCacheRepo
from src.service.settings.config import Settings

logger = logging.getLogger(__name__)


@dataclass
class DownloaderService:
    """Класс, предоставляющий функциональность поиска и загрузки треков."""

    external_repository: list[DownloaderAbstractRepo]
    cache_repository: DownloaderCacheRepo
    settings: Settings

    def _get_repo(self, repo_alias: str) -> DownloaderAbstractRepo:
        """
        Возвращает репозиторий по его алиасу.

        :param repo_alias: Алиас репозитория.
        :return: Экземпляр репозитория.
        :raises StopIteration: Если репозиторий с таким алиасом не найден.
        """
        return next(x for x in self.external_repository if x.alias == repo_alias)

    async def find_tracks_on_phrase(
        self,
        phrase: str,
        bot: Bot,
        chat_id: int,
        skip_repo_alias: str | None = None,
    ) -> RepoTracks | None:
        """
        Ищет треки по заданной фразе в доступных репозиториях.

        При поиске отображается индикатор загрузки. Если репозиторий был указан как `skip_repo_alias`,
        он будет пропущен при поиске.

        :param phrase: Фраза для поиска треков.
        :param bot: Экземпляр бота Aiogram для отправки сообщений.
        :param chat_id: ID чата, в котором будет отображаться индикатор.
        :param skip_repo_alias: (Опционально) Алиас репозитория, который нужно пропустить.
        :return: Найденные треки в формате `RepoTracks` или `None`, если ничего не найдено.
        """
        logger.debug(f"Searching for tracks on phrase '{phrase}'")

        # Сортируем репозитории по приоритету
        self.external_repository.sort(key=lambda x: x.priority)

        if skip_repo_alias:
            skip_repo = self._get_repo(skip_repo_alias)
            skip_index_repo = self.external_repository.index(skip_repo) + 1
            self.external_repository = self.external_repository[skip_index_repo:]

        for _idx, repo in enumerate(self.external_repository):
            logger.debug(f"Поиск в источнике {repo.alias}, {phrase=}")
            try:
                spinner_msg = """
                🔎 Ищу трек…{spinner_item}\n(это может занять несколько секунд ⏳)
                """
                founded_tracks = await processing_msg(
                    repo.find_tracks_on_phrase,
                    (phrase, chat_id),
                    bot=bot,
                    chat_id=chat_id,
                    spinner_msg=spinner_msg,
                )
                if founded_tracks:
                    return RepoTracks(
                        tracks=[Track.model_validate(x) for x in founded_tracks],
                        repo_alias=repo.alias,
                    )
            except Exception as error:
                logger.exception(f"Ошибка в {repo.alias}: {error}")  # noqa: TRY401
                continue
        return None

    async def download_track(
        self,
        download_params: DownloadTrackParams,
        bot: Bot,
        chat_id: int,
    ) -> Path:
        """
        Загружает трек на сервер.

        Генерируется уникальное имя файла, после чего происходит загрузка через указанный репозиторий.
        Если возникает ошибка, она логгируется и выбрасывается исключение.

        :param download_params: Параметры загрузки трека.
        :param bot: Экземпляр бота Aiogram для отправки сообщений.
        :param chat_id: ID чата, в котором будет отображаться индикатор.
        :return: Путь к загруженному файлу.
        :raises DownloadError: Если произошла ошибка загрузки.
        :raises Exception: Если произошла другая ошибка.
        """
        logger.debug(
            f"Downloading track '{download_params.url}', repo: '{download_params.repo_alias}'",
        )
        track_path = Path(gettempdir()) / f"{uuid.uuid4()}.mp3"

        repo = self._get_repo(download_params.repo_alias)

        url_track = await self.cache_repository.get_track_url(
            download_params.url,
            chat_id=chat_id,
        )

        try:
            await processing_msg(
                repo.download_track,
                (bot, url_track, track_path),
                bot=bot,
                chat_id=chat_id,
                spinner_msg="🛬 Загружаем трек на сервер…{spinner_item}",
            )
        except DownloadError:
            logger.exception("YouTrack не смог скачать аудио-дорожку")
            raise
        except Exception as error:
            logger.exception(error)  # noqa: TRY401
            raise
        else:
            return track_path
