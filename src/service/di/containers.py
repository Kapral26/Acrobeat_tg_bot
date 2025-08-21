from dishka import AsyncContainer, make_async_container

from src.service.di.providers import (
    CliperProvider,
    ConfigProvider,
    DatabaseProvider,
    DownloaderProvider,
    RedisProvider,
    UserProvider,
)


def create_container() -> AsyncContainer:
    containers = [
        ConfigProvider(),
        DatabaseProvider(),
        RedisProvider(),
        DownloaderProvider(),
        CliperProvider(),
        UserProvider(),
    ]

    return make_async_container(*containers)
