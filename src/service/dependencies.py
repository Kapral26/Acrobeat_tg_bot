"""Модуль с провайдерами сервисных зависимостей."""

from dishka import FromDishka, Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from src.service.settings.config import Settings


class ConfigProvider(Provider):
    """Провайдер для получения конфигурации приложения."""

    @provide(scope=Scope.APP)
    async def get_config(self) -> Settings:
        """Возвращает экземпляр объекта настроек приложения."""
        return Settings()


class DatabaseProvider(Provider):
    """
    Провайдер для работы с базой данных.

    Отвечает за создание асинхронного движка и фабрики сессий.
    """

    @provide(scope=Scope.REQUEST)
    def get_async_engine(
        self,
        settings: FromDishka[Settings],
    ) -> AsyncEngine:
        """
        Создаёт и возвращает асинхронный движок SQLAlchemy.

        :param settings: Объект настроек, из которого берётся DSN для подключения к БД.
        :return: Экземпляр AsyncEngine.
        """
        from sqlalchemy.ext.asyncio import create_async_engine  # noqa: PLC0415

        return create_async_engine(
            url=settings.postgres.async_database_dsn,
            echo=settings.debug,
            pool_size=5,
            max_overflow=10,
        )

    @provide(scope=Scope.REQUEST)
    def get_async_session_factory(self, engine: AsyncEngine) -> async_sessionmaker:
        """
        Возвращает фабрику асинхронных сессий SQLAlchemy.

        :param engine: Асинхронный движок SQLAlchemy.
        :return: Фабрика асинхронных сессий.
        """
        return async_sessionmaker(engine)


class RedisProvider(Provider):
    """
    Провайдер для работы с Redis.

    Отвечает за создание клиентского соединения с Redis.
    """

    @provide(scope=Scope.REQUEST)
    async def get_redis_client(
        self,
        settings: FromDishka[Settings],
    ) -> Redis:
        """
        Создаёт и возвращает клиент Redis.

        :param settings: Объект настроек, из которого берутся параметры подключения к Redis.
        :return: Экземпляр клиента Redis.
        """
        return Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db,
        )
