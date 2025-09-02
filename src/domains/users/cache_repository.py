from dataclasses import dataclass

from redis.asyncio import Redis

from src.domains.tracks.track_name.schemas import TrackNamePartSchema
from src.service.cache.base_cache_repository import RedisClientWrapper


@dataclass
class UserCacheRepository(RedisClientWrapper):
    redis_client: Redis
    user_track_names_key: str = "track_names:{user_id}"

    def __post_init__(self):
        # Обязательно вызываем инициализацию родительского класса
        super().__init__(self.redis_client)

    async def set_user_track_names(
        self, user_id: int, track_names: list[TrackNamePartSchema]
    ) -> None:
        track_names_json = [x.model_dump_json() for x in track_names]
        async with self.redis_client.pipeline() as pipe:
            key = self.user_track_names_key.format(user_id=user_id)
            await pipe.delete(key)
            await pipe.lpush(key, *track_names_json)
            await pipe.expire(key, 120)
            await pipe.execute()

    async def get_user_track_names(
        self, user_id: int
    ) -> list[TrackNamePartSchema] | None:
        key = self.user_track_names_key.format(user_id=user_id)
        if not await self.redis_client.exists(key):
            return None

        async with self.redis_client.pipeline() as pipe:
            await pipe.lrange(key, 0, -1)
            response = await pipe.execute()
            track_names = [
                TrackNamePartSchema.model_validate_json(x.decode("utf8"))
                for x in response[0]
            ]
            return track_names
