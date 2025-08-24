from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import Sequence, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.tracks.track_storage.models import DownloadedTrack
from src.domains.tracks.track_storage.schemas import TrackCreateSchema


@dataclass
class TrackStorageRepository:
    session_factory: Callable[[], AsyncSession]

    async def insert_downloaded_track(self, downloaded_track_data: TrackCreateSchema):
        async with self.session_factory() as session:
            stmt = insert(DownloadedTrack).values(**downloaded_track_data)
            await session.execute(stmt)
            await session.commit()

    async def delete_downloaded_track(self, track_id: int) -> bool:
        async with self.session_factory() as session:
            track = await session.get(DownloadedTrack, track_id)
            if not track:
                return False
            try:
                await session.delete(track)
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()
                return True

    async def get_downloaded_track_by_id(self, track_id: int) -> DownloadedTrack | None:
        async with self.session_factory() as session:
            return await session.get(DownloadedTrack, track_id)

    async def get_downloaded_track_by_source_url(
        self, source_url: str
    ) -> DownloadedTrack | None:
        async with self.session_factory() as session:
            stmt = select(DownloadedTrack).where(
                DownloadedTrack.source_url == source_url
            )
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_downloaded_tracks_by_title(
        self, title: str
    ) -> Sequence[DownloadedTrack]:
        async with self.session_factory() as session:
            stmt = select(DownloadedTrack).where(
                DownloadedTrack.title.ilike(f"%{title}%")
            )
            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_downloaded_tracks_by_artist(
        self, artist: str
    ) -> Sequence[DownloadedTrack]:
        async with self.session_factory() as session:
            stmt = select(DownloadedTrack).where(
                DownloadedTrack.artist.ilike(f"%{artist}%")
            )
            result = await session.execute(stmt)
            return result.scalars().all()

    async def search_downloaded_tracks(
        self, downloaded_track_data: TrackCreateSchema
    ) -> Sequence[DownloadedTrack]:
        async with self.session_factory() as session:
            stmt = select(DownloadedTrack)

            # Фильтруем только по тем полям, которые были переданы
            if downloaded_track_data.title is not None:
                stmt = stmt.where(DownloadedTrack.title == downloaded_track_data.title)
            if downloaded_track_data.artist is not None:
                stmt = stmt.where(
                    DownloadedTrack.artist == downloaded_track_data.artist
                )
            if downloaded_track_data.source_url is not None:
                stmt = stmt.where(
                    DownloadedTrack.source_url == downloaded_track_data.source_url
                )

            result = await session.execute(stmt)
            return result.scalar_one_or_none()
