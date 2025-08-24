from dishka import FromDishka, Provider, Scope, provide
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.domains.tracks.track_storage.repository import TrackStorageRepository
from src.domains.tracks.track_storage.service import TrackStorageService


class TrackStorageProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_repo(
        self,
        session_factory: FromDishka[async_sessionmaker],
    ) -> TrackStorageRepository:
        return TrackStorageRepository(session_factory=session_factory)

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self, repo: FromDishka[TrackStorageRepository]
    ) -> TrackStorageService:
        return TrackStorageService(repo)
