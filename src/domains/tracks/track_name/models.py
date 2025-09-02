"""
Модуль `models.py` содержит определение SQLAlchemy-модели для сущности `TrackNameRegistry`.

Описывает структуру таблицы `track_name_registry`, которая связывает пользователей с частями названий треков,
используемыми в системе.
"""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.service.database.database import Base

if TYPE_CHECKING:
    from src.domains.users.models import User


class TrackNameRegistry(Base):
    """
    Модель для хранения связей между пользователями и частями названий треков.

    Представляет запись в таблице `track_name_registry`, где хранится информация о:
    - пользователе, связанном с частью названия трека;
    - самой части названия (например, "Иванов_ИО_1990").
    """

    __tablename__ = "track_name_registry"

    id: Mapped[int] = mapped_column(
        BigInteger(),
        primary_key=True,
        index=True,
        comment="Уникальный идентификатор записи",
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID пользователя, связанный с частью названия трека",
    )
    track_part: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Часть названия трека (например, 'Иванов_ИО_1990')",
    )

    # Связь с моделью пользователя
    user: Mapped["User"] = relationship(
        "User", back_populates="track_names", lazy="joined"
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "track_part", name="uix_user_track_part"
        ),  # Уникальность пары (пользователь, часть названия)
    )
