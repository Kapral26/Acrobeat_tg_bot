from dishka import Provider, \
    provide, \
    Scope, \
    FromDishka
from redis.asyncio import Redis

from src.service.downloader.cach_repository import DownloaderCacheRepo
from src.service.downloader.repository import DownloaderRepoYT, \
    DownloaderRepoPinkamuz, \
    TelegramDownloaderRepo
from src.service.downloader.service import DownloaderService
from src.service.settings.config import Settings


class DownloaderProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_cache_repository(
        self,
        redis_client: FromDishka[Redis],
    ) -> DownloaderCacheRepo:
        return DownloaderCacheRepo(redis_client=redis_client)

    @provide(scope=Scope.REQUEST)
    async def get_repository_yt(
        self,
        settings: FromDishka[Settings],
        cache_repository: FromDishka[DownloaderCacheRepo],
    ) -> DownloaderRepoYT:
        return DownloaderRepoYT(settings, cache_repository)

    @provide(scope=Scope.REQUEST)
    async def get_repository_pinkamuz(
        self,
        settings: FromDishka[Settings],
        cache_repository: FromDishka[DownloaderCacheRepo],
    ) -> DownloaderRepoPinkamuz:
        return DownloaderRepoPinkamuz(settings, cache_repository)

    @provide(scope=Scope.REQUEST)
    async def get_repository_telegram(
        self,
    ) -> TelegramDownloaderRepo:
        return TelegramDownloaderRepo()

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self,
        repository_yt: FromDishka[DownloaderRepoYT],
        repository_pinkamuz: FromDishka[DownloaderRepoPinkamuz],
        repository_telegram: FromDishka[TelegramDownloaderRepo],
        settings: FromDishka[Settings],
        cache_repository: FromDishka[DownloaderCacheRepo],
    ) -> DownloaderService:
        return DownloaderService(
            external_repository=[
                repository_pinkamuz,
                repository_yt,
                repository_telegram,
            ],
            cache_repository=cache_repository,
            settings=settings,
        )
