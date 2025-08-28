from dishka import FromDishka, Provider, Scope, provide

from src.domains.tracks.track_cliper.service import TrackCliperService
from src.service.cliper.repository import TrackCliperRepo


class TrackCliperProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_service(
        self,
        cliper_repo: FromDishka[TrackCliperRepo],
    ) -> TrackCliperService:
        return TrackCliperService(cliper_repo=cliper_repo)
