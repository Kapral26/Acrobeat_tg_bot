from dataclasses import dataclass

from redis.asyncio import Redis

from src.service.cache.base_cache_repository import RedisClientWrapper


@dataclass
class TrackCacheRepository(RedisClientWrapper):
    redis_client: Redis
    cliper_messages_key: str = "cliper_messages:{user_id}"

    def __post_init__(self):
        super().__init__(self.redis_client)

    async def get_cliper_messages_to_delete(self, user_id: int) -> list[int]:
        key = self.cliper_messages_key.format(user_id=user_id)
        raw_items = await self.lrange(key, 0, -1)
        return [int(item.decode("utf-8")) for item in raw_items]

    async def add_cliper_message_to_delete(self, user_id: int, message_id: int) -> None:
        key = self.cliper_messages_key.format(user_id=user_id)
        # Добавляем элемент в конец списка
        await self.rpush(key, str(message_id))

    async def set_cliper_messages_to_delete(
        self, user_id: int, messages: list[int]
    ) -> None:
        key = self.cliper_messages_key.format(user_id=user_id)
        # Очищаем старый список и добавляем новые элементы
        await self.delete(key)
        if messages:
            await self.rpush(key, *[str(mid) for mid in messages])
        # Установка TTL (опционально)
        await self.expire(key, 60)

    async def delete_cliper_messages_to_delete(self, user_id: int) -> None:
        key = self.cliper_messages_key.format(user_id=user_id)
        await self.delete(key)
