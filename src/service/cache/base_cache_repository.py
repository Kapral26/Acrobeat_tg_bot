from dataclasses import dataclass

from redis import Redis
from redis.asyncio import Redis

from src.service.cache.abc import RedisBase


class RedisClientWrapper(RedisBase):
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def set(self, key: str, value: str, ttl: int) -> None:
        exists = await self.redis_client.exists(key)
        if exists:
            await self.redis_client.delete(key)

        await self.redis_client.setex(name=key, time=ttl, value=value)

    async def get(self, key: str) -> str | None:
        data = await self.redis_client.get(key)
        return data.decode("utf-8") if data else None

    async def delete(self, key: str) -> None:
        await self.redis_client.delete(key)

    async def expire(self, key: str, ttl: int) -> None:
        await self.redis_client.expire(key, ttl)

    # 🔹 Работа со списками (lists)

    async def rpush(self, key: str, *values: str) -> int:
        """Добавляет элементы в конец списка"""
        return await self.redis_client.rpush(key, *values)

    async def lpush(self, key: str, *values: str) -> int:
        """Добавляет элементы в начало списка"""
        return await self.redis_client.lpush(key, *values)

    async def lrange(self, key: str, start: int, end: int) -> list[str]:
        """Возвращает диапазон элементов из списка"""
        raw_items = await self.redis_client.lrange(key, start, end)
        return [item.decode("utf-8") for item in raw_items]

    async def llen(self, key: str) -> int:
        """Возвращает длину списка"""
        return await self.redis_client.llen(key)

    async def lpop(self, key: str) -> str | None:
        """Удаляет и возвращает первый элемент списка"""
        item = await self.redis_client.lpop(key)
        return item.decode("utf-8") if item else None

    async def rpop(self, key: str) -> str | None:
        """Удаляет и возвращает последний элемент списка"""
        item = await self.redis_client.rpop(key)
        return item.decode("utf-8") if item else None

    async def lrem(self, key: str, count: int, value: str) -> int:
        """Удаляет элементы из списка по значению"""
        return await self.redis_client.lrem(key, count, value)

    async def lset(self, key: str, index: int, value: str) -> bool:
        """Заменяет значение элемента списка по индексу"""
        return await self.redis_client.lset(key, index, value)

    async def ltrim(self, key: str, start: int, stop: int) -> bool:
        """Оставляет только указанный диапазон элементов списка"""
        return await self.redis_client.ltrim(key, start, stop)


@dataclass
class BaseMsgCleanerRepository(RedisClientWrapper):
    redis_client: Redis

    @property
    def messages_key(self) -> str:
        return "{user_id}"

    def __post_init__(self):
        super().__init__(self.redis_client)

    async def get_messages_to_delete(self, user_id: int) -> list[int]:
        key = self.messages_key.format(user_id=user_id)
        raw_items = await self.lrange(key, 0, -1)
        return [int(item) for item in raw_items]

    async def add_message_to_delete(self, user_id: int, message_id: int) -> None:
        key = self.messages_key.format(user_id=user_id)
        # Добавляем элемент в конец списка
        await self.rpush(key, str(message_id))
        await self.expire(key, 120)

    async def delete_messages_to_delete(self, user_id: int) -> None:
        key = self.messages_key.format(user_id=user_id)
        await self.delete(key)
