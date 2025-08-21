"""Содержит код для настройки соединения с базой данных, включая параметры подключения и инициализацию SQLAlchemy."""

from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""

    created_at: Mapped[datetime] = (
        mapped_column(
            default=datetime.now
        ),
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        onupdate=datetime.now,
    )
