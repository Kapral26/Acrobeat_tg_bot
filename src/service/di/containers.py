from dishka import AsyncContainer, make_async_container

from src.domains.tracks.dependencies import TrackProvider
from src.domains.tracks.track_cliper.dependencies import TrackCliperProvider
from src.domains.tracks.track_name.dependencies import TrackNameProvider
from src.domains.tracks.track_request.dependencies import (
    TrackRequestProvider,
)
from src.domains.tracks.track_search.dependencies import TrackSearchProvider
from src.domains.users.dependencies import UserProvider
from src.service.cliper.dependencies import CliperProvider
from src.service.dependencies import (
    ConfigProvider,
    DatabaseProvider,
    RedisProvider,
)
from src.service.downloader.dependencies import DownloaderProvider


def create_container() -> AsyncContainer:
    containers = [
        ConfigProvider(),
        DatabaseProvider(),
        RedisProvider(),
        DownloaderProvider(),
        CliperProvider(),
        UserProvider(),
        TrackRequestProvider(),
        TrackProvider(),
        TrackSearchProvider(),
        TrackCliperProvider(),
        TrackNameProvider(),
    ]

    return make_async_container(*containers)
