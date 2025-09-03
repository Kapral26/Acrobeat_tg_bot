import pytest

from src.domains.tracks.track_cliper.utils import calculate_clip_duration, is_valid_time_format


@pytest.mark.parametrize("time_str,expected", [
    ("00:00", True),
    ("23:59", True),
    ("24:00", False),
    ("12:60", False),
    ("9:05", True),
    ("9:5", False),
    ("-1:00", False),
    ("12:34", True),
    ("abc", False),
])
def test_is_valid_time_format(time_str, expected):
    assert is_valid_time_format(time_str) is expected

@pytest.mark.parametrize("start,end,expected", [
    ("01:00", "02:00", 60),
    ("00:00", "00:30", 30),
    ("10:00", "10:59", 59),
])
def test_calculate_clip_duration_valid(start, end, expected):
    assert calculate_clip_duration(start, end) == expected

@pytest.mark.parametrize("start,end", [
    ("02:00", "01:00"),
    ("00:30", "00:00"),
])
def test_calculate_clip_duration_invalid(start, end):
    with pytest.raises(ValueError):
        calculate_clip_duration(start, end)

