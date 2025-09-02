"""
Модуль `base_cache_repository.py` содержит реализацию базового репозитория для работы с кэшем на основе Redis.

Реализует интерфейс `RedisBase`, предоставляя методы для хранения, извлечения и удаления данных в Redis.
Также добавлены методы для работы со списками, что позволяет использовать Redis как структурированное хранилище.
"""

from dataclasses import dataclass

from redis.asyncio import Redis

from src.service.cache.abc import RedisBase


class RedisClientWrapper(RedisBase):
    """
    Базовая реализация интерфейса `RedisBase`.

    Обеспечивает доступ к Redis через асинхронные операции и поддерживает основные функции:
    - установка значений с TTL;
    - получение значений;
    - удаление ключей;
    - работа со списками (lists).
    """

    def __init__(self, redis_client: Redis):
        """
        Инициализация экземпляра.

        :param redis_client: Асинхронный клиент Redis.
        """
        self.redis_client = redis_client

    async def set(self, key: str, value: str, ttl: int) -> None:
        """
        Устанавливает значение по указанному ключу с заданным сроком жизни (TTL).

        Если ключ уже существует, он будет удалён перед установкой нового значения.

        :param key: Ключ, по которому будет храниться значение.
        :param value: Значение, которое нужно сохранить.
        :param ttl: Время жизни ключа в секундах.
        """
        exists = await self.redis_client.exists(key)
        if exists:
            await self.redis_client.delete(key)

        await self.redis_client.setex(name=key, time=ttl, value=value)

    async def get(self, key: str) -> str | None:
        """
        Получает значение по указанному ключу.

        :param key: Ключ, по которому нужно получить значение.
        :return: Найденное значение или `None`, если ключ не существует.
        """
        data = await self.redis_client.get(key)
        return data.decode("utf-8") if data else None

    async def delete(self, key: str) -> None:
        """
        Удаляет значение по указанному ключу.

        :param key: Ключ, который нужно удалить.
        """
        await self.redis_client.delete(key)

    async def expire(self, key: str, ttl: int) -> None:
        """
        Устанавливает время жизни (TTL) для существующего ключа.

        :param key: Ключ, для которого устанавливается TTL.
        :param ttl: Время жизни ключа в секундах.
        """
        await self.redis_client.expire(key, ttl)

    # 🔹 Работа со списками (lists)

    async def rpush(self, key: str, *values: str) -> int:
        """Добавляет элементы в конец списка."""
        return await self.redis_client.rpush(key, *values)

    async def lpush(self, key: str, *values: str) -> int:
        """Добавляет элементы в начало списка."""
        return await self.redis_client.lpush(key, *values)

    async def lrange(self, key: str, start: int, end: int) -> list[str]:
        """Возвращает диапазон элементов из списка."""
        raw_items = await self.redis_client.lrange(key, start, end)
        return [item.decode("utf-8") for item in raw_items]

    async def llen(self, key: str) -> int:
        """Возвращает длину списка."""
        return await self.redis_client.llen(key)

    async def lpop(self, key: str) -> str | None:
        """
        Удаляет и возвращает первый элемент списка.

        :param key: Ключ Redis.
        :return: Декодированное значение или None, если список пуст.
        """
        item: bytes | None = await self.redis_client.lpop(key)
        return item.decode("utf-8") if item else None

    async def rpop(self, key: str) -> str | None:
        """
        Удаляет и возвращает последний элемент списка.

        :param key: Ключ Redis.
        :return: Декодированное значение или None, если список пуст.
        """
        item: bytes | None = await self.redis_client.rpop(key)
        return item.decode("utf-8") if item else None

    async def lrem(self, key: str, count: int, value: str) -> int:
        """Удаляет элементы из списка по значению."""
        return await self.redis_client.lrem(key, count, value)

    async def lset(self, key: str, index: int, value: str) -> str:
        """Заменяет значение элемента списка по индексу."""
        return await self.redis_client.lset(key, index, value)

    async def ltrim(self, key: str, start: int, stop: int) -> str:
        """Оставляет только указанный диапазон элементов списка."""
        return await self.redis_client.ltrim(key, start, stop)


@dataclass
class BaseMsgCleanerRepository(RedisClientWrapper):
    """
    Реализация репозитория для хранения ID сообщений, которые необходимо удалить позже.

    Использует Redis для временного хранения и управления списком ID сообщений.
    """

    redis_client: Redis

    @property
    def messages_key(self) -> str:
        """Формат ключа для хранения ID сообщений."""
        return "messages_to_delete:{user_id}"

    def __post_init__(self):
        """Вызывается после инициализации для настройки родительского класса."""
        super().__init__(self.redis_client)

    async def get_messages_to_delete(self, user_id: int) -> list[int]:
        """
        Получает список ID сообщений, которые нужно удалить.

        :param user_id: ID пользователя, чьи сообщения нужно получить.
        :return: Список ID сообщений.
        """
        key = self.messages_key.format(user_id=user_id)
        raw_items = await self.lrange(key, 0, -1)
        return [int(item) for item in raw_items]

    async def add_message_to_delete(self, user_id: int, message_id: int) -> None:
        """
        Добавляет ID сообщения в список для удаления.

        :param user_id: ID пользователя.
        :param message_id: ID сообщения, которое нужно удалить.
        """
        key = self.messages_key.format(user_id=user_id)
        await self.rpush(key, str(message_id))
        await self.expire(key, 30)  # истёкнет через 30 секунд

    async def delete_messages_to_delete(self, user_id: int) -> None:
        """
        Очищает список ID сообщений для указанного пользователя.

        :param user_id: ID пользователя.
        """
        key = self.messages_key.format(user_id=user_id)
        await self.delete(key)
