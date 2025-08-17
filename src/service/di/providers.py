import logging

from dishka import FromDishka, Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from src.service.cliper.repository import TrackCliperRepo
from src.service.cliper.service import TrackCliperService
from src.service.downloader.repository import DownloaderRepo
from src.service.downloader.service import DownloaderService
from src.service.settings.config import Settings


class LoggerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_logger(self) -> logging.Logger:
        return logging.getLogger("app_logger")


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_config(self) -> Settings:
        return Settings()


class DatabaseProvider(Provider):
    """Провайдер для работы с базой данных."""

    @provide(scope=Scope.REQUEST)
    def get_async_engine(
        self,
        settings: FromDishka[Settings],
    ) -> AsyncEngine:
        """Возвращает асинхронный движок SQLAlchemy."""
        from sqlalchemy.ext.asyncio import create_async_engine

        return create_async_engine(
            url=settings.postgres.async_database_dsn,
            echo=settings.debug,
            pool_size=5,
            max_overflow=10,
        )

    @provide(scope=Scope.REQUEST)
    def get_async_session_factory(self, engine: AsyncEngine) -> async_sessionmaker:
        """Возвращает фабрику асинхронных сессий."""
        return async_sessionmaker(engine)


class DownloaderProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_repository(
        self,
        settings: FromDishka[Settings],
    ) -> DownloaderRepo:
        return DownloaderRepo(settings)

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self,
        repository: FromDishka[DownloaderRepo],
        settings: FromDishka[Settings],
        logger: FromDishka[logging.Logger],
    ) -> DownloaderService:
        return DownloaderService(repository, settings, logger)


class CliperProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_repo(self) -> TrackCliperRepo:
        return TrackCliperRepo()

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self, repo: FromDishka[TrackCliperRepo]
    ) -> TrackCliperService:
        return TrackCliperService(repo)
