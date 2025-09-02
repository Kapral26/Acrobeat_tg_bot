"""
Модуль `dependencies.py` содержит DI-провайдер для модуля управления временными сообщениями при работе с названиями треков.

Регистрирует зависимости, связанные с:
- репозиторием для хранения идентификаторов сообщений в Redis;
- сервисом для управления временными сообщениями.
"""

from dishka import FromDishka, Provider, Scope, provide
from redis.asyncio import Redis

from src.domains.tracks.track_name.cache_repository import TrackNameMsgCleanerRepository
from src.domains.tracks.track_name.message_cleanup import TrackNameMsgCleanerService


class TrackNameProvider(Provider):
    """
    Класс-провайдер для внедрения зависимостей модуля управления временными сообщениями.

    Регистрирует:
    - `TrackNameMsgCleanerRepository` — для взаимодействия с Redis;
    - `TrackNameMsgCleanerService` — для реализации логики очистки сообщений.
    """

    @provide(scope=Scope.REQUEST)
    async def get_cache_cleaner_repo(
        self,
        redis_client: FromDishka[Redis],
    ) -> TrackNameMsgCleanerRepository:
        """
        Возвращает экземпляр репозитория для работы с кэшем временных сообщений.

        :param redis_client: Асинхронный клиент Redis для хранения данных.
        :return: Экземпляр `TrackNameMsgCleanerRepository`.
        """
        return TrackNameMsgCleanerRepository(redis_client=redis_client)

    @provide(scope=Scope.REQUEST)
    async def get_cleaner_service(
        self,
        cache_repository: FromDishka[TrackNameMsgCleanerRepository],
    ) -> TrackNameMsgCleanerService:
        """
        Возвращает экземпляр сервиса для управления временными сообщениями.

        :param cache_repository: Репозиторий для хранения идентификаторов сообщений.
        :return: Экземпляр `TrackNameMsgCleanerService`.
        """
        return TrackNameMsgCleanerService(cache_repository=cache_repository)
