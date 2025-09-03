
import pytest

from src.service.cache.base_cache_repository import BaseCacheRepository


class DummyCache(BaseCacheRepository):
    async def get(self, key):
        return f"value:{key}"
    async def set(self, key, value):
        return True
    async def delete(self, key):
        return True

@pytest.mark.asyncio
async def test_cache_get_set_delete():
    cache = DummyCache()
    key = "test_key"
    value = "test_value"
    # set
    result = await cache.set(key, value)
    assert result is True
    # get
    val = await cache.get(key)
    assert val == f"value:{key}"
    # delete
    result = await cache.delete(key)
    assert result is True

