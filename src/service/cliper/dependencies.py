from dishka import Provider, \
    provide, \
    Scope, \
    FromDishka

from src.service.cliper.repository import TrackCliperRepo
from src.service.cliper.service import CliperService


class CliperProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_repo(self) -> TrackCliperRepo:
        return TrackCliperRepo()

    @provide(scope=Scope.REQUEST)
    async def get_service(
        self, repo: FromDishka[TrackCliperRepo]
    ) -> CliperService:
        return CliperService(repo)
