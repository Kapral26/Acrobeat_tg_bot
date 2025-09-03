import pytest

from src.domains.tracks.schemas import Track


@pytest.mark.parametrize(
    "duration,expected_minutes,expected_seconds",
    [
        (0, 0, 0),
        (59, 0, 59),
        (60, 1, 0),
        (125, 2, 5),
    ],
)
def test_track_minutes_seconds(duration, expected_minutes, expected_seconds):
    track = Track(title="Test", duration=duration, webpage_url="url")
    assert track.minutes == expected_minutes
    assert track.seconds == expected_seconds


def test_track_validation():
    track = Track(title="Test", duration=123, webpage_url="url")
    assert track.title == "Test"
    assert track.duration == 123
    assert track.webpage_url == "url"

