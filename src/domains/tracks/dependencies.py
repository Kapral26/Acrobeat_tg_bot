"""Модуль `dependencies.py` содержит DI-провайдер для модуля треков."""

from dishka import FromDishka, Provider, Scope, provide

from src.domains.tracks.service import TrackService
from src.domains.tracks.track_cliper.message_cleanup import TrackClipMsgCleanerService
from src.domains.tracks.track_cliper.service import TrackCliperService
from src.service.downloader.service import DownloaderService


class TrackProvider(Provider):
    """
    Класс-провайдер для внедрения зависимостей модуля треков.

    Регистрирует:
    - `TrackService` — для работы с треками (загрузка, обработка, отправка).
    """

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self,
        downloader_service: FromDishka[DownloaderService],
        track_cliper_service: FromDishka[TrackCliperService],
        cleaner_service: FromDishka[TrackClipMsgCleanerService],
    ) -> TrackService:
        """
        Возвращает экземпляр сервиса для работы с треками.

        :param downloader_service: Сервис для загрузки треков из источников.
        :param track_cliper_service: Сервис для обработки аудиофайлов.
        :param cleaner_service: Сервис для удаления временных сообщений.
        :return: Экземпляр `TrackService`.
        """
        return TrackService(
            downloader_service=downloader_service,
            track_cliper_service=track_cliper_service,
            cleaner_service=cleaner_service,
        )
