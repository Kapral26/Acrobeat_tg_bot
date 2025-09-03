from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.service.cliper.repository import TrackCliperRepo


@pytest.mark.asyncio
async def test_cut_audio_fragment():
    fake_input = Path("/tmp/fake_input.mp3")
    start_sec = 1.0
    duration_sec = 2.0
    fake_output = Path("/tmp/fake_output.mp3")

    with patch("src.service.cliper.repository.tempfile.mkstemp", return_value=(None, str(fake_output))):
        with patch("src.service.cliper.repository.ffmpeg.input") as mock_input:
            mock_stream = MagicMock()
            mock_input.return_value = mock_stream
            mock_stream.output.return_value = mock_stream
            mock_stream.overwrite_output.return_value = mock_stream
            mock_stream.run.return_value = None

            result = await TrackCliperRepo.cut_audio_fragment(fake_input, start_sec, duration_sec)
            assert result == fake_output
            mock_input.assert_called_once_with(str(fake_input), ss=start_sec, t=duration_sec)
            mock_stream.output.assert_called_once()
            mock_stream.run.assert_called_once()
