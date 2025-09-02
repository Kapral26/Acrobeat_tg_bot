"""
Модуль `dependencies.py` отвечает за инверсию зависимостей для компонентов системы загрузки треков.

Создаёт провайдер (Dependency Provider) на основе библиотеки `dishka`, который регистрирует:
    - репозитории для поиска и загрузки музыки;
    - сервис для обработки запросов;
    - зависимости между ними (Redis, конфигурация);

Этот модуль используется в контейнере зависимостей (`create_container`) для автоматического управления жизненным циклом объектов.
"""

from dishka import FromDishka, Provider, Scope, provide
from redis.asyncio import Redis

from src.service.downloader.cache_repository import DownloaderCacheRepo
from src.service.downloader.repository import (
    DownloaderRepoHitmo,
    DownloaderRepoPinkamuz,
    DownloaderRepoYT,
    TelegramDownloaderRepo,
)
from src.service.downloader.service import DownloaderService
from src.service.settings.config import Settings


class DownloaderProvider(Provider):
    """
    Класс-провайдер, реализующий DI-логику для компонентов скачивания треков.

    Отвечает за создание экземпляров репозиториев и сервиса, а также их внедрение в нужные места приложения.
    """

    @provide(scope=Scope.REQUEST)
    async def get_cache_repository(
        self,
        redis_client: FromDishka[Redis],
    ) -> DownloaderCacheRepo:
        """
        Создаёт и возвращает кэширующий репозиторий, использующий Redis.

        :param redis_client: Клиент Redis, предоставляемый из DI-контейнера.
        :return: Экземпляр DownloaderCacheRepo.
        """
        return DownloaderCacheRepo(redis_client=redis_client)

    @provide(scope=Scope.REQUEST)
    async def get_repository_yt(
        self,
        settings: FromDishka[Settings],
        cache_repository: FromDishka[DownloaderCacheRepo],
    ) -> DownloaderRepoYT:
        """
        Создаёт и возвращает репозиторий для работы с YouTube.

        :param settings: Объект настроек.
        :param cache_repository: Кэширующий репозиторий.
        :return: Экземпляр DownloaderRepoYT.
        """
        return DownloaderRepoYT(settings, cache_repository)

    @provide(scope=Scope.REQUEST)
    async def get_repository_pinkamuz(
        self,
        settings: FromDishka[Settings],
        cache_repository: FromDishka[DownloaderCacheRepo],
    ) -> DownloaderRepoPinkamuz:
        """
        Создаёт и возвращает репозиторий для работы с сайтом Pinkamuz.

        :param settings: Объект настроек.
        :param cache_repository: Кэширующий репозиторий.
        :return: Экземпляр DownloaderRepoPinkamuz.
        """
        return DownloaderRepoPinkamuz(settings, cache_repository)

    @provide(scope=Scope.REQUEST)
    async def get_repository_hitmo(
        self,
        settings: FromDishka[Settings],
        cache_repository: FromDishka[DownloaderCacheRepo],
    ) -> DownloaderRepoHitmo:
        """
        Создаёт и возвращает репозиторий для работы с Hitmotop.

        :param settings: Объект настроек.
        :param cache_repository: Кэширующий репозиторий.
        :return: Экземпляр DownloaderRepoHitmo.
        """
        return DownloaderRepoHitmo(settings, cache_repository)

    @provide(scope=Scope.REQUEST)
    async def get_repository_telegram(
        self,
    ) -> TelegramDownloaderRepo:
        """
        Создаёт и возвращает репозиторий для работы с Telegram.

        :return: Экземпляр TelegramDownloaderRepo.
        """
        return TelegramDownloaderRepo()

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self,
        repository_yt: FromDishka[DownloaderRepoYT],
        repository_pinkamuz: FromDishka[DownloaderRepoPinkamuz],
        repository_telegram: FromDishka[TelegramDownloaderRepo],
        repository_hitmo: FromDishka[DownloaderRepoHitmo],
        settings: FromDishka[Settings],
        cache_repository: FromDishka[DownloaderCacheRepo],
    ) -> DownloaderService:
        """
        Создаёт и возвращает сервис для поиска и загрузки треков.

        Сервис использует зарегистрированные репозитории, чтобы обеспечить поиск и загрузку треков из разных источников.

        :param repository_yt: Репозиторий для YouTube.
        :param repository_pinkamuz: Репозиторий для Pinkamuz.
        :param repository_telegram: Репозиторий для Telegram.
        :param repository_hitmo: Репозиторий для Hitmotop.
        :param settings: Объект настроек.
        :param cache_repository: Кэширующий репозиторий.
        :return: Экземпляр DownloaderService.
        """
        return DownloaderService(
            external_repository=[
                repository_pinkamuz,
                repository_yt,
                repository_telegram,
                repository_hitmo,
            ],
            cache_repository=cache_repository,
            settings=settings,
        )
