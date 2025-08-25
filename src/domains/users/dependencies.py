from dishka import Provider, \
    provide, \
    Scope, \
    FromDishka
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.domains.users.cache_repository import UserCacheRepository
from src.domains.users.repository import UserRepository
from src.domains.users.services import UserService


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
