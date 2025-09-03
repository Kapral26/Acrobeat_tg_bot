from unittest.mock import AsyncMock

import pytest

from src.domains.tracks.track_request.service import TrackRequestService


@pytest.mark.asyncio
async def test_insert_track_request() -> None:
    """
    Проверяет, что TrackRequestService вызывает insert_track_request у репозитория.
    """
    repo = AsyncMock()
    service = TrackRequestService(track_request_repository=repo)
    await service.insert_track_request(user_id=1, query_text="test query")
    repo.insert_track_request.assert_awaited()
