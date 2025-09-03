from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domains.tracks.track_request.repository import TrackRequestRepository
from src.domains.tracks.track_request.schemas import TrackRequestSchema


@pytest.mark.asyncio
async def test_insert_track_request() -> None:
    """
    Проверяет, что insert_track_request вызывает execute и commit у сессии.
    """
    session = AsyncMock()
    session_factory = MagicMock(return_value=session)
    repo = TrackRequestRepository(session_factory=session_factory)
    data = TrackRequestSchema(user_id=1, query_text="test query")
    session.execute.return_value = MagicMock()
    await repo.insert_track_request(data)
    session.execute.assert_awaited()
    session.commit.assert_awaited()
