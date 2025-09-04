"""
Модуль `cache_repository.py` содержит реализацию кэширующего репозитория
 для временного хранения ссылок на музыкальные треки.

Используется Redis для хранения ссылок, что позволяет сократить объём данных,
 передаваемых в callback_data inline-кнопок бота.
"""

import secrets
from dataclasses import dataclass
from enum import IntEnum

from redis.asyncio import Redis


class CacheTTL(IntEnum):
    """Перечисление для определения времён жизни ключей в Redis."""

    TEN_MINUTES = 60 * 10
    TWO_MINUTES = 60 * 2
    ONE_HOUR = 60 * 60
    ONE_DAY = 60 * 60 * 24


@dataclass
class DownloaderCacheRepo:
    """
    Класс для работы с кэшированием ссылок на музыкальные треки.

    Использует Redis для хранения временных ссылок, чтобы обойти ограничение длины callback_data в Telegram API.
    """

    redis_client: Redis

    async def get_track_url(self, track_url_id: str, chat_id: int) -> str:
        """
        Получает оригинальную ссылку на трек по её идентификатору из Redis.

        :param track_url_id: Уникальный идентификатор ссылки.
        :param chat_id: ID чата, используется как префикс ключа для изоляции данных разных пользователей.
        :return: Оригинальная ссылка на трек или исходный идентификатор, если ссылка не найдена.
        """
        key = f"{chat_id}_track_url:{track_url_id}"
        data = await self.redis_client.get(key)
        return data.decode("utf8") if data else track_url_id

    async def set_track_url(self, track_url: str, chat_id: int) -> str:
        """
        Сохраняет ссылку на трек в Redis под уникальным идентификатором.

        Это необходимо, так как Telegram API ограничивает длину callback_data до 64 байт, и длинные ссылки на аудиофайлы
        не могут быть переданы напрямую. Вместо этого генерируется короткий идентификатор, который позже используется
        для получения оригинальной ссылки.

        :param track_url: Оригинальная ссылка на трек.
        :param chat_id: ID чата, используется как префикс ключа для изоляции данных разных пользователей.
        :return: Сгенерированный уникальный идентификатор ссылки.
        """
        track_url_id = secrets.token_hex(8)
        key = f"{chat_id}_track_url:{track_url_id}"
        await self.redis_client.setex(
            key,
            CacheTTL.TWO_MINUTES.value,
            track_url,
        )
        return track_url_id
