from datetime import datetime, timedelta

from sqlalchemy import TIMESTAMP, BigInteger, ForeignKey, String, Text, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domains.users.models import User
from src.service.database.database import Base


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    artist: Mapped[str | None] = mapped_column(String(255))
    duration: Mapped[int | None] = mapped_column()  # в секундах
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime]
    platform: Mapped[str | None] = mapped_column(String(50))  # youtube, soundcloud, vk
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow
    )

    # связи
    clips: Mapped[list["Clip"]] = relationship(
        back_populates="track", cascade="all, delete"
    )
    requests: Mapped[list["TrackRequest"]] = relationship(back_populates="track")


@event.listens_for(Track, "before_insert")
def generate_expires_at(mapper, connection, target: Track):
    """Устанавливает время срок хранение трека."""
    one_hour = 60 * 60
    target.expires_at = datetime.now() + timedelta(seconds=one_hour)


class TrackRequest(Base):
    __tablename__ = "track_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    track_id: Mapped[int] = mapped_column(ForeignKey(Track.id))

    # связи
    track: Mapped["Track"] = relationship(back_populates="requests")
    user: Mapped["User"] = relationship(back_populates="track_requests")


class Clip(Base):
    __tablename__ = "clips"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id"), nullable=False)
    clip_url: Mapped[str] = mapped_column(Text, nullable=False)
    clip_start_sec: Mapped[int] = mapped_column(nullable=False)
    clip_duration: Mapped[int] = mapped_column(nullable=False)

    # связи
    track: Mapped["Track"] = relationship(back_populates="clips")
