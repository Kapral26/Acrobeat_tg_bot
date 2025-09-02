"""
Модуль `dependencies.py` содержит DI-провайдер для модуля обработки аудиообрезки треков.

Регистрирует зависимости, связанные с:
- сервисом обработки аудиофайлов;
- репозиторием для хранения временных сообщений в Redis;
- сервисом управления временными сообщениями.
"""

from dishka import FromDishka, Provider, Scope, provide
from redis.asyncio import Redis

from src.domains.tracks.track_cliper.cache_repository import ClipMsgCleanerRepository
from src.domains.tracks.track_cliper.message_cleanup import TrackClipMsgCleanerService
from src.domains.tracks.track_cliper.service import TrackCliperService
from src.service.cliper.repository import TrackCliperRepo


class TrackCliperProvider(Provider):
    """
    Класс-провайдер для внедрения зависимостей модуля обработки аудиообрезки.

    Регистрирует:
    - `TrackCliperService` — для выполнения операций обработки аудиофайлов;
    - `ClipMsgCleanerRepository` — для взаимодействия с Redis при работе с
    временными сообщениями;
    - `TrackClipMsgCleanerService` — для реализации логики очистки временных данных.
    """

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self,
        cliper_repo: FromDishka[TrackCliperRepo],
    ) -> TrackCliperService:
        """
        Возвращает экземпляр сервиса для обработки аудиообрезки.

        :param cliper_repo: Репозиторий для низкоуровневых операций с аудиофайлами.
        :return: Экземпляр `TrackCliperService`.
        """
        return TrackCliperService(cliper_repo=cliper_repo)

    @provide(scope=Scope.REQUEST)
    async def get_cache_cleaner_repo(
        self,
        redis_client: FromDishka[Redis],
    ) -> ClipMsgCleanerRepository:
        """
        Возвращает экземпляр репозитория для хранения временных сообщений в Redis.

        :param redis_client: Асинхронный клиент Redis для хранения данных.
        :return: Экземпляр `ClipMsgCleanerRepository`.
        """
        return ClipMsgCleanerRepository(redis_client=redis_client)

    @provide(scope=Scope.REQUEST)
    async def get_cleaner_service(
        self,
        cache_repository: FromDishka[ClipMsgCleanerRepository],
    ) -> TrackClipMsgCleanerService:
        """
        Возвращает экземпляр сервиса для управления временными сообщениями.

        :param cache_repository: Репозиторий для работы с кэшем временных данных.
        :return: Экземпляр `TrackClipMsgCleanerService`.
        """
        return TrackClipMsgCleanerService(cache_repository=cache_repository)
