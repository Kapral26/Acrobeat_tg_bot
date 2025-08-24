from dishka import AsyncContainer, make_async_container

from src.domains.tracks.track_storage.dependencies import TrackStorageProvider
from src.domains.tracks.track_storage.track_request_storage.dependencies import (
    TrackRequestProvider,
)
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
        TrackStorageProvider(),
    ]

    return make_async_container(*containers)
