"""
Модуль `models.py` содержит определение SQLAlchemy-модели для сущности `TrackRequest`.

Описывает структуру таблицы `track_requests`, хранящей историю поисковых запросов пользователей на треки.
"""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.service.database.database import Base

if TYPE_CHECKING:
    from src.domains.users.models import User


class TrackRequest(Base):
    """
    Модель для хранения истории поисковых запросов пользователей на музыкальные треки.

    Представляет запись в таблице `track_requests`, где хранится информация о:
    - пользователе, совершившем запрос;
    - тексте поискового запроса.
    """

    __tablename__ = "track_requests"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    query_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Связь с моделью пользователя
    user: Mapped["User"] = relationship(back_populates="track_requests", lazy="joined")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "query_text",
            name="uq_user_query",
        ),  # Уникальность пары (пользователь, запрос)
    )
