from dishka import AsyncContainer, make_async_container

from src.service.di.providers import (
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
    ]

    return make_async_container(*containers)