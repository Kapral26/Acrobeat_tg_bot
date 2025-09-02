"""
Модуль `dependencies.py` содержит DI-провайдер для модуля управления запросами на треки.

Регистрирует зависимости, связанные с:
- репозиторием для работы с историей поисковых запросов;
- сервисом для обработки логики взаимодействия с данными о запросах;
"""

from dishka import FromDishka, Provider, Scope, provide
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.domains.tracks.track_request.repository import (
    TrackRequestRepository,
)
from src.domains.tracks.track_request.service import (
    TrackRequestService,
)


class TrackRequestProvider(Provider):
    """
    Класс-провайдер для внедрения зависимостей модуля управления запросами на треки.

    Регистрирует:
    - `TrackRequestRepository` — для работы с базой данных;
    - `TrackRequestService` — для реализации бизнес-логики обработки запросов.
    """

    @provide(scope=Scope.REQUEST)
    async def get_repo(
        self,
        session_factory: FromDishka[async_sessionmaker],
    ) -> TrackRequestRepository:
        """
        Возвращает экземпляр репозитория для работы с историей запросов.

        :param session_factory: Фабрика асинхронных сессий SQLAlchemy.
        :return: Экземпляр `TrackRequestRepository`.
        """
        return TrackRequestRepository(session_factory=session_factory)

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self, repo: FromDishka[TrackRequestRepository]
    ) -> TrackRequestService:
        """
        Возвращает экземпляр сервиса для обработки запросов на треки.

        :param repo: Репозиторий для работы с базой данных.
        :return: Экземпляр `TrackRequestService`.
        """
        return TrackRequestService(repo)
