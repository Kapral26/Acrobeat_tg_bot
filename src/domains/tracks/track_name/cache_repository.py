from dataclasses import dataclass

from redis.asyncio import Redis

from src.service.cache.base_cache_repository import BaseMsgCleanerRepository


@dataclass
class TrackNameMsgCleanerRepository(BaseMsgCleanerRepository):
    redis_client: Redis

    @property
    def messages_key(self) -> str:
        return "track_name_messages:{user_id}"
