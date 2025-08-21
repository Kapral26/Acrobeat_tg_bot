from dishka import FromDishka, Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from src.domains.users.cache_repository import UserCacheRepository
from src.domains.users.repository import UserRepository
from src.domains.users.services import UserService
from src.service.cliper.repository import TrackCliperRepo
from src.service.cliper.service import TrackCliperService
from src.service.downloader.cach_repository import DownloaderCacheRepo
from src.service.downloader.repository import (
    DownloaderRepoPinkamuz,
    DownloaderRepoYT,
    TelegramDownloaderRepo,
)
from src.service.downloader.service import DownloaderService
from src.service.settings.config import Settings


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


class RedisProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_redis_client(
        self,
        settings: FromDishka[Settings],
    ) -> Redis:
        return Redis(
            host=settings.redis.host, port=settings.redis.port, db=settings.redis.db
        )


class DownloaderProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_cache_repository(
        self,
        redis_client: FromDishka[Redis],
    ) -> DownloaderCacheRepo:
        return DownloaderCacheRepo(redis_client=redis_client)

    @provide(scope=Scope.REQUEST)
    async def get_repository_yt(
        self,
        settings: FromDishka[Settings],
        cache_repository: FromDishka[DownloaderCacheRepo],
    ) -> DownloaderRepoYT:
        return DownloaderRepoYT(settings, cache_repository)

    @provide(scope=Scope.REQUEST)
    async def get_repository_pinkamuz(
        self,
        settings: FromDishka[Settings],
        cache_repository: FromDishka[DownloaderCacheRepo],
    ) -> DownloaderRepoPinkamuz:
        return DownloaderRepoPinkamuz(settings, cache_repository)

    @provide(scope=Scope.REQUEST)
    async def get_repository_telegram(
        self,
    ) -> TelegramDownloaderRepo:
        return TelegramDownloaderRepo()

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self,
        repository_yt: FromDishka[DownloaderRepoYT],
        repository_pinkamuz: FromDishka[DownloaderRepoPinkamuz],
        repository_telegram: FromDishka[TelegramDownloaderRepo],
        settings: FromDishka[Settings],
        cache_repository: FromDishka[DownloaderCacheRepo],
    ) -> DownloaderService:
        return DownloaderService(
            external_repository=[
                repository_pinkamuz,
                repository_yt,
                repository_telegram,
            ],
            cache_repository=cache_repository,
            settings=settings,
        )


class CliperProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_repo(self) -> TrackCliperRepo:
        return TrackCliperRepo()

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self, repo: FromDishka[TrackCliperRepo]
    ) -> TrackCliperService:
        return TrackCliperService(repo)


class UserProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_user_repo(
        self,
        session_factory: FromDishka[async_sessionmaker],
    ) -> UserRepository:
        return UserRepository(session_factory)

    @provide(scope=Scope.REQUEST)
    async def get_user_cache_repo(
        self,
        redis_client: FromDishka[Redis],
    ) -> UserCacheRepository:
        return UserCacheRepository(redis_client=redis_client)

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self,
        user_repo: FromDishka[UserRepository],
        user_cache_repository: FromDishka[UserCacheRepository],
    ) -> UserService:
        return UserService(
            user_repository=user_repo,
            user_cache_repository=user_cache_repository,
        )
