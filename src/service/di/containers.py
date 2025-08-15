from dishka import AsyncContainer, make_async_container

from src.service.di.providers import LoggerProvider, \
    ConfigProvider, DatabaseProvider


def create_container() -> AsyncContainer:
    containers = [
        LoggerProvider(),
        ConfigProvider(),
        DatabaseProvider(),
    ]

    return make_async_container(*containers)