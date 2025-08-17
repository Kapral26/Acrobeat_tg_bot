from dishka import AsyncContainer, make_async_container

from src.service.di.providers import (
    CliperProvider,
    ConfigProvider,
    DatabaseProvider,
    DownloaderProvider,
    LoggerProvider,
)


def create_container() -> AsyncContainer:
    containers = [
        LoggerProvider(),
        ConfigProvider(),
        DatabaseProvider(),
        DownloaderProvider(),
        CliperProvider(),
    ]

    return make_async_container(*containers)
