from types import SimpleNamespace

import pytest

from src.domains.tracks.filters import YouTubeLinkFilter


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text,expected",
    [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
        ("https://youtu.be/dQw4w9WgXcQ", True),
        ("youtube.com/watch?v=dQw4w9WgXcQ", True),
        ("https://google.com", False),
        ("not a link", False),
        (None, False),
    ],
)
async def test_youtube_link_filter(text, expected):
    filter_ = YouTubeLinkFilter()
    message = SimpleNamespace(text=text)
    result = await filter_(message)
    assert result is expected
