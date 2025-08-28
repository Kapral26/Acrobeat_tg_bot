import secrets
from dataclasses import dataclass
from enum import IntEnum

from redis.asyncio import Redis


class CacheTTL(IntEnum):
    TEN_MINUTES = 60 * 10
    ONE_HOUR = 60 * 60
    ONE_DAY = 60 * 60 * 24


@dataclass
class DownloaderCacheRepo:
    redis_client: Redis

    async def get_track_url(self, track_url_id: str, chat_id: int) -> str:
        key = f"{chat_id}_track_url:{track_url_id}"
        data = await self.redis_client.get(key)
        return data.decode("utf8") if data else track_url_id

    async def set_track_url(self, track_url: str, chat_id: int) -> str:
        """
        Метод для временного хранения ссылки на трек.
        Требуется т.к. callback_data inline-кнопки в боте может передавать,
        не большее 64-байт.

        Используется только для конкретного репозитория треков.

        :param track_url: Существующая ссылка на трек
        :return: callback_data со ссылкой на скачивание трека.
        """
        track_url_id = secrets.token_hex(8)
        key = f"{chat_id}_track_url:{track_url_id}"
        await self.redis_client.setex(key, CacheTTL.TEN_MINUTES.value, track_url)
        return track_url_id
