from sqlalchemy import BigInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domains.users.models import User
from src.service.database.database import Base


class TrackNameRegistry(Base):
    __tablename__ = "track_name_registry"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, index=True)
    user_id: Mapped[int]
    track_part: Mapped[String] = mapped_column(String(255), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="track_names")


    __table_args__ = (
        UniqueConstraint("user_id", "track_part", name="uix_user_track_part"),
    )
