from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.domains.tracks.service import TrackService


@pytest.mark.asyncio
async def test_send_track():
    bot = AsyncMock()
    chat_id = 123
    file_name = "test.mp3"
    path = Path("/tmp/test.mp3")
    # Мокаем открытие файла
    with patch("aiofiles.open", AsyncMock()):
        await TrackService.__send_track(path, bot, chat_id, file_name)
    bot.send_audio.assert_awaited()
