from dishka import FromDishka, Provider, Scope, provide
from redis.asyncio import Redis

from src.domains.tracks.track_name.cache_repository import TrackNameMsgCleanerRepository
from src.domains.tracks.track_name.message_cleanup import TrackNameMsgCleanerService


class TrackNameProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_cache_cleaner_repo(
        self,
        redis_client: FromDishka[Redis],
    ) -> TrackNameMsgCleanerRepository:
        return TrackNameMsgCleanerRepository(redis_client=redis_client)

    @provide(scope=Scope.REQUEST)
    async def get_cleaner_service(
        self,
        cache_repository: FromDishka[TrackNameMsgCleanerRepository],
    ) -> TrackNameMsgCleanerService:
        return TrackNameMsgCleanerService(cache_repository=cache_repository)
