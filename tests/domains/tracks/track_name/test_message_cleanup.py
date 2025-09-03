from unittest.mock import MagicMock

from src.domains.tracks.track_name.message_cleanup import TrackNameMsgCleanerService


def test_track_name_msg_cleaner_service_init():
    cache_repo = MagicMock()
    service = TrackNameMsgCleanerService(cache_repository=cache_repo)
    assert service.cache_repository is cache_repo

