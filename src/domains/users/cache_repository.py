"""
Модуль `cache_repository.py` содержит реализацию кэширующего репозитория для пользователей.

Работает с Redis и предоставляет функциональность хранения и получения данных о частях названий треков,
связанных с конкретным пользователем.
"""

from dataclasses import dataclass

from redis.asyncio import Redis

from src.domains.tracks.track_name.schemas import TrackNamePartSchema
from src.service.cache.base_cache_repository import RedisClientWrapper


@dataclass
class UserCacheRepository(RedisClientWrapper):
    """
    Класс-репозиторий для кэширования данных о пользователях в Redis.

    Реализует операции хранения и получения списка частей названий треков, связанных с пользователем.
    """

    redis_client: Redis
    user_track_names_key: str = "track_names:{user_id}"

    def __post_init__(self):
        """
        Выполняет инициализацию родительского класса `RedisClientWrapper`.

        Обеспечивает корректное наследование функциональности работы с Redis.
        """
        super().__init__(self.redis_client)

    async def set_user_track_names(
        self, user_id: int, track_names: list[TrackNamePartSchema]
    ) -> None:
        """
        Сохраняет список частей названий треков пользователя в Redis.

        :param user_id: ID пользователя.
        :param track_names: Список объектов `TrackNamePartSchema`.
        """
        track_names_json = [x.model_dump_json() for x in track_names]
        async with self.redis_client.pipeline() as pipe:
            key = self.user_track_names_key.format(user_id=user_id)
            await pipe.delete(key)
            await pipe.lpush(key, *track_names_json)
            await pipe.expire(key, 30)
            await pipe.execute()

    async def get_user_track_names(
        self, user_id: int
    ) -> list[TrackNamePartSchema] | None:
        """
        Получает список частей названий треков пользователя из Redis.

        :param user_id: ID пользователя.
        :return: Список объектов `TrackNamePartSchema` или `None`, если ключ не существует.
        """
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
