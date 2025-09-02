"""
Модуль `dependencies.py` содержит DI-провайдер для модуля пользователей.

Регистрирует зависимости, связанные с:
- репозиторием пользователей (работа с базой данных);
- кэширующим репозиторием (работа с Redis);
- сервисом обработки пользовательских данных.
"""

from dishka import FromDishka, Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.domains.users.cache_repository import UserCacheRepository
from src.domains.users.repository import UserRepository
from src.domains.users.services import UserService


class UserProvider(Provider):
    """
    Класс-провайдер для внедрения зависимостей модуля пользователей.

    Регистрирует:
    - `UserRepository` — для работы с базой данных;
    - `UserCacheRepository` — для хранения и получения данных в Redis;
    - `UserService` — для реализации бизнес-логики.
    """

    @provide(scope=Scope.REQUEST)
    async def get_user_repo(
        self,
        session_factory: FromDishka[async_sessionmaker],
    ) -> UserRepository:
        """
        Возвращает экземпляр репозитория для работы с пользователями.

        :param session_factory: Фабрика асинхронных сессий SQLAlchemy.
        :return: Экземпляр `UserRepository`.
        """
        return UserRepository(session_factory)

    @provide(scope=Scope.REQUEST)
    async def get_user_cache_repo(
        self,
        redis_client: FromDishka[Redis],
    ) -> UserCacheRepository:
        """
        Возвращает экземпляр кэширующего репозитория для пользователей.

        :param redis_client: Асинхронный клиент Redis.
        :return: Экземпляр `UserCacheRepository`.
        """
        return UserCacheRepository(redis_client=redis_client)

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self,
        user_repo: FromDishka[UserRepository],
        user_cache_repository: FromDishka[UserCacheRepository],
    ) -> UserService:
        """
        Возвращает экземпляр сервиса для работы с пользователями.

        :param user_repo: Репозиторий для работы с базой данных.
        :param user_cache_repository: Кэширующий репозиторий.
        :return: Экземпляр `UserService`.
        """
        return UserService(
            user_repository=user_repo,
            user_cache_repository=user_cache_repository,
        )
