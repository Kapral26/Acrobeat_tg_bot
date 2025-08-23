from dishka import FromDishka, Provider, Scope, provide
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.domains.tracks.track_storage.track_request_storage.repository import (
    TrackRequestStorageRepository,
)
from src.domains.tracks.track_storage.track_request_storage.service import (
    TrackRequestStorageService,
)


class TrackRequestProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_repo(
        self,
        session_factory: FromDishka[async_sessionmaker],
    ) -> TrackRequestStorageRepository:
        return TrackRequestStorageRepository(session_factory=session_factory)

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self, repo: FromDishka[TrackRequestStorageRepository]
    ) -> TrackRequestStorageService:
        return TrackRequestStorageService(repo)
