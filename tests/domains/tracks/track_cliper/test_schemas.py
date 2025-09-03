import pytest

from src.domains.tracks.track_cliper.schemas import ClipPeriodSchema


@pytest.mark.parametrize(
    "start,finish,expected_duration",
    [
        ("00:00", "00:30", 30),
        ("01:00", "02:00", 60),
        ("10:00", "10:59", 59),
    ],
)
def test_clip_period_schema_valid(start, finish, expected_duration):
    schema = ClipPeriodSchema(start=start, finish=finish)
    assert schema.duration_sec == expected_duration

@pytest.mark.parametrize(
    "start,finish",
    [
        ("02:00", "01:00"),
        ("00:30", "00:00"),
        ("abc", "00:10"),
        ("00:10", "xyz"),
        ("12:60", "13:00"),
    ],
)
def test_clip_period_schema_invalid(start, finish):
    with pytest.raises(ValueError):
        ClipPeriodSchema(start=start, finish=finish)

