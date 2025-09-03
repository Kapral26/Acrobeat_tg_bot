from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from src.domains.tracks.track_cliper.schemas import ClipPeriodSchema
from src.domains.tracks.track_cliper.service import TrackCliperService


@pytest.mark.asyncio
async def test_clip_track():
    cliper_repo = AsyncMock()
    bot = AsyncMock()
    chat_id = 123
    track_path = Path("/tmp/test.mp3")
    clip_period = ClipPeriodSchema(start="00:00", finish="00:30")
    service = TrackCliperService(cliper_repo=cliper_repo)
    cliper_repo.cut_audio_fragment.return_value = track_path
    result = await service.clip_track(track_path, bot, chat_id, clip_period)
    cliper_repo.cut_audio_fragment.assert_awaited()
    assert result == track_path

