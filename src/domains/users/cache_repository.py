from dataclasses import dataclass

from redis import Redis

from src.domains.tracks.track_name.schemas import TrackNamePartSchema


@dataclass
class UserCacheRepository:
    redis_client: Redis
    user_track_names_key: str = "track_names:{user_id}"

    async def set_user_track_names(
        self, user_id: int, track_names: list[TrackNamePartSchema]
    ) -> None:
        track_names_json = [x.model_dump_json() for x in track_names]
        async with self.redis_client.pipeline() as pipe:
            key = self.user_track_names_key.format(user_id=user_id)
            # Удалить старые задачи, если они существуют
            await pipe.delete(key)
            # Добавить новый список задач в Redis (в виде JSON-строк)
            await pipe.lpush(key, *track_names_json)
            # Указываю время жизни
            await pipe.expire(key, 120)
            # Выполнить команды в pipeline
            await pipe.execute()

    async def get_user_track_names(
        self, user_id: int
    ) -> list[TrackNamePartSchema] | None:
        key = self.user_track_names_key.format(user_id=user_id)
        if not self.redis_client.exists(key):
            return None

        async with self.redis_client.pipeline() as pipe:
            await pipe.lrange(key, 0, -1)
            response = await pipe.execute()
            track_names = [
                TrackNamePartSchema.model_validate_json(x.decode("utf8"))
                for x in response[0]
            ]
            return track_names
