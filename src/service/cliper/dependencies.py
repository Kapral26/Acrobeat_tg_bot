from dishka import Provider, Scope, provide

from src.service.cliper.repository import TrackCliperRepo


class CliperProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_repo(self) -> TrackCliperRepo:
        return TrackCliperRepo()

