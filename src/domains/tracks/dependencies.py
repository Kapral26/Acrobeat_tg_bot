from dishka import FromDishka, Provider, Scope, provide
from redis.asyncio import Redis

from src.domains.tracks.cache_repository import TrackCacheRepository
from src.domains.tracks.service import TrackService
from src.domains.tracks.track_cliper.service import TrackCliperService
from src.service.downloader.service import DownloaderService


class TrackProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def get_cache(
            self,
            redis_client: FromDishka[Redis],
    ) -> TrackCacheRepository:
        return TrackCacheRepository(redis_client)

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self,
        downloader_service: FromDishka[DownloaderService],
        track_cliper_service: FromDishka[TrackCliperService],
        cache_repository: FromDishka[TrackCacheRepository],
    ) -> TrackService:
        return TrackService(
            downloader_service=downloader_service,
            track_cliper_service=track_cliper_service,
            cache_repository=cache_repository
        )
