from dishka import FromDishka, Provider, Scope, provide
from redis.asyncio import Redis

from src.domains.tracks.track_cliper.cache_repository import ClipMsgCleanerRepository
from src.domains.tracks.track_cliper.message_cleanup import TrackClipMsgCleanerService
from src.domains.tracks.track_cliper.service import TrackCliperService
from src.service.cliper.repository import TrackCliperRepo


class TrackCliperProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_service(
        self,
        cliper_repo: FromDishka[TrackCliperRepo],
    ) -> TrackCliperService:
        return TrackCliperService(cliper_repo=cliper_repo)

    @provide(scope=Scope.REQUEST)
    async def get_cache_cleaner_repo(
        self,
        redis_client: FromDishka[Redis],
    ) -> ClipMsgCleanerRepository:
        return ClipMsgCleanerRepository(redis_client=redis_client)

    @provide(scope=Scope.REQUEST)
    async def get_cleaner_service(
        self,
        cache_repository: FromDishka[ClipMsgCleanerRepository],
    ) -> TrackClipMsgCleanerService:
        return TrackClipMsgCleanerService(cache_repository=cache_repository)
