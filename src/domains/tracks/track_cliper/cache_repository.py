"""
Модуль `cache_repository.py` содержит реализацию репозитория для работы с кэшем
 временных сообщений, связанных с обработкой аудиообрезки треков.

Обеспечивает хранение идентификаторов сообщений в Redis для последующей
 очистки после завершения операций обработки аудиофайлов.
"""

from dataclasses import dataclass

from redis.asyncio import Redis

from src.service.cache.base_cache_repository import BaseMsgCleanerRepository


@dataclass
class ClipMsgCleanerRepository(BaseMsgCleanerRepository):
    """
    Репозиторий для хранения идентификаторов временных сообщений, связанных с аудиообрезкой.

    Использует Redis для асинхронного хранения данных. Ключи формируются по шаблону `cliper_messages:{user_id}`,
    где `{user_id}` — уникальный идентификатор пользователя.

    Наследует методы базового класса `BaseMsgCleanerRepository` для:
    - добавления идентификаторов сообщений;
    - получения списка сообщений для очистки;
    - удаления временных данных.
    """

    redis_client: Redis

    @property
    def messages_key(self) -> str:
        """
        Формирует ключ для хранения идентификаторов сообщений в Redis.

        Пример: `cliper_messages:123456789`, где `123456789` — ID пользователя.

        :return: Строка с ключом для Redis.
        """
        return "cliper_messages:{user_id}"
