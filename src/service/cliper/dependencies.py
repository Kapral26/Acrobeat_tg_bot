from dishka import Provider, \
    provide, \
    Scope, \
    FromDishka

from src.service.cliper.repository import TrackCliperRepo
from src.service.cliper.service import TrackCliperService


class CliperProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_repo(self) -> TrackCliperRepo:
        return TrackCliperRepo()

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self, repo: FromDishka[TrackCliperRepo]
    ) -> TrackCliperService:
        return TrackCliperService(repo)
