from unittest.mock import MagicMock

from src.domains.tracks.track_cliper.message_cleanup import TrackClipMsgCleanerService


def test_track_clip_msg_cleaner_service_init():
    cache_repo = MagicMock()
    service = TrackClipMsgCleanerService(cache_repository=cache_repo)
    assert service.cache_repository is cache_repo

