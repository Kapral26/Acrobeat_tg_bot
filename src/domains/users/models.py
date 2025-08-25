from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import BigInteger, String

from src.service.database.database import Base

if TYPE_CHECKING:
    from src.domains.tracks.track_name.models import TrackNameRegistry
    from src.domains.tracks.track_request.models import TrackRequest


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(128), nullable=True)

    track_names: Mapped[list["TrackNameRegistry"]] = relationship(
        "TrackNameRegistry", back_populates="user", cascade="all, delete-orphan"
    )

    track_requests: Mapped[list["TrackRequest"]] = relationship(back_populates="user")
