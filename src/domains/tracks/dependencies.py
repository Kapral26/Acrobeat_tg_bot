from dishka import FromDishka, Provider, Scope, provide

from src.domains.tracks.service import TrackService
from src.domains.tracks.track_cliper.message_cleanup import TrackClipMsgCleanerService
from src.domains.tracks.track_cliper.service import TrackCliperService
from src.service.downloader.service import DownloaderService


class TrackProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_service(
        self,
        downloader_service: FromDishka[DownloaderService],
        track_cliper_service: FromDishka[TrackCliperService],
        cleaner_service: FromDishka[TrackClipMsgCleanerService],
    ) -> TrackService:
        return TrackService(
            downloader_service=downloader_service,
            track_cliper_service=track_cliper_service,
            cleaner_service=cleaner_service,
        )
