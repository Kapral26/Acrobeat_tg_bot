from sqlalchemy import BigInteger, \
    ForeignKey, \
    Text, \
    UniqueConstraint
from sqlalchemy.orm import Mapped, \
    mapped_column, \
    relationship

from src.service.database.database import Base


class TrackRequest(Base):
    __tablename__ = "track_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)

    # связи
    user: Mapped["User"] = relationship(back_populates="track_requests")

    __table_args__ = (UniqueConstraint("user_id", "query_text", name="uq_user_query"),)
