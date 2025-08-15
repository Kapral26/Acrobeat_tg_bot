import logging

from dishka import FromDishka, Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

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
            url=settings.async_database_dsn,
            echo=settings.debug,
            pool_size=5,
            max_overflow=10,
        )

    @provide(scope=Scope.REQUEST)
    def get_async_session_factory(self, engine: AsyncEngine) -> async_sessionmaker:
        """Возвращает фабрику асинхронных сессий."""
        return async_sessionmaker(engine)

