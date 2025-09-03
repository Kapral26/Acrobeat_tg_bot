from unittest.mock import AsyncMock, patch

import pytest

import src.service.database.database as db_module


@pytest.mark.asyncio
async def test_get_connection_success():
    mock_pool = AsyncMock()
    with patch.object(db_module, "asyncpg", autospec=True) as mock_asyncpg:
        mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)
        pool = await db_module.get_connection_pool(dsn="postgresql://user:pass@localhost/db")
        assert pool is mock_pool
        mock_asyncpg.create_pool.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_connection_fail():
    with patch.object(db_module, "asyncpg", autospec=True) as mock_asyncpg:
        mock_asyncpg.create_pool = AsyncMock(side_effect=Exception("fail"))
        with pytest.raises(Exception):
            await db_module.get_connection_pool(dsn="postgresql://user:pass@localhost/db")
