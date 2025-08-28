from dataclasses import dataclass

from redis.asyncio import Redis

from src.service.cache.base_cache_repository import BaseMsgCleanerRepository


@dataclass
class ClipMsgCleanerRepository(BaseMsgCleanerRepository):
    redis_client: Redis

    @property
    def messages_key(self) -> str:
        return "cliper_messages:{user_id}"


