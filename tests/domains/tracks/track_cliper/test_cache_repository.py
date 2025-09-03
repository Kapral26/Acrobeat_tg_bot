from unittest.mock import AsyncMock

import pytest

from src.domains.tracks.track_cliper.cache_repository import ClipMsgCleanerRepository


@pytest.mark.asyncio
def test_messages_key():
    redis_client = AsyncMock()
    repo = ClipMsgCleanerRepository(redis_client=redis_client)
    assert repo.messages_key == "cliper_messages:{user_id}"

