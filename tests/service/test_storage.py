from unittest.mock import AsyncMock, patch

import pytest

import src.service.storage as storage_module


@pytest.mark.asyncio
async def test_get_storage_redis():
    with patch.object(storage_module, "Settings") as mock_settings:
        mock_settings.return_value.redis.enabled = True
        mock_storage = AsyncMock()
        with patch.object(storage_module, "RedisStorage", return_value=mock_storage):
            storage = storage_module.get_storage()
            assert storage is mock_storage


@pytest.mark.asyncio
async def test_get_storage_memory():
    with patch.object(storage_module, "Settings") as mock_settings:
        mock_settings.return_value.redis.enabled = False
        mock_storage = AsyncMock()
        with patch.object(storage_module, "MemoryStorage", return_value=mock_storage):
            storage = storage_module.get_storage()
            assert storage is mock_storage
