from abc import ABC, abstractmethod


class RedisBase(ABC):
    @abstractmethod
    async def set(self, key: str, value: str, ttl: int) -> None: ...

    @abstractmethod
    async def get(self, key: str) -> str | None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...
