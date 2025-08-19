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

    async def get_track_url(self, track_url_id: str) -> str:
        key = f"track_url:{track_url_id}"
        data = await self.redis_client.get(key)
        if data:
            return data.decode("utf8")
        else:
            raise ValueError("Не найдено")

    async def set_track_url(self, track_url: str) -> str:
        track_url_id = secrets.token_hex(8)
        key = f"track_url:{track_url_id}"
        await self.redis_client.setex(key, CacheTTL.TEN_MINUTES.value, track_url)
        return track_url_id
