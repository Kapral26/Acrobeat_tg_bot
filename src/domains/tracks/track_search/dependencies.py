from dishka import Provider, Scope, provide

from src.domains.tracks.track_search.service import TrackSearchService


class TrackSearchProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_service(
        self,
    ) -> TrackSearchService:
        return TrackSearchService()
