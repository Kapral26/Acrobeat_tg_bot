from dishka import FromDishka, Provider, Scope, provide
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.domains.tracks.track_request.repository import (
    TrackRequestRepository,
)
from src.domains.tracks.track_request.service import (
    TrackRequestService,
)


class TrackRequestProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_repo(
        self,
        session_factory: FromDishka[async_sessionmaker],
    ) -> TrackRequestRepository:
        return TrackRequestRepository(session_factory=session_factory)

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self, repo: FromDishka[TrackRequestRepository]
    ) -> TrackRequestService:
        return TrackRequestService(repo)
