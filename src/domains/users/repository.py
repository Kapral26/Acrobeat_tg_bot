"""
Модуль `repository.py` содержит реализацию репозитория для работы с пользователями в базе данных.

Реализует CRUD-операции над моделью `User`, а также обеспечивает взаимодействие с моделью `TrackNameRegistry`.
"""

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.tracks.track_name.models import TrackNameRegistry
from src.domains.users.models import User
from src.domains.users.schemas import UsersSchema

logger = logging.getLogger(__name__)


@dataclass
class UserRepository:
    """
    Репозиторий для работы с моделью `User`.

    Обеспечивает операции:
    - регистрации новых пользователей;
    - получения информации о пользователях;
    - управления связанными данными (например, частями названий треков).
    """

    session_factory: Callable[[], AsyncSession]

    async def insert_new_user(self, user_data: UsersSchema) -> None:
        """
        Регистрация нового пользователя в базе данных.

        :param user_data: Данные пользователя.
        """
        async with self.session_factory() as session:
            stmt = insert(User).values(
                id=user_data.id,
                username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
            )
            try:
                await session.execute(stmt)
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()

    async def get_users(self) -> Sequence[User]:
        """
        Получает всех зарегистрированных пользователей.

        :return: Список объектов модели `User`.
        """
        async with self.session_factory() as session:
            query_result = await session.execute(select(User))
            return query_result.scalars().all()

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Получает пользователя по его ID.

        :param user_id: ID пользователя.
        :return: Объект модели `User` или `None`, если пользователь не найден.
        """
        async with self.session_factory() as session:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Получает пользователя по его никнейму.

        :param username: Никнейм пользователя.
        :return: Объект модели `User` или `None`, если пользователь не найден.
        """
        async with self.session_factory() as session:
            # Сбрасываем кэш SQLAlchemy
            session.expire_all()
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_user_track_names(
        self,
        user_id: int,
    ) -> Sequence[TrackNameRegistry] | list[Any]:
        """
        Получает список частей названий треков, связанных с пользователем.

        :param user_id: ID пользователя.
        :return: Список объектов модели `TrackNameRegistry` или пустой список.
        """
        async with self.session_factory() as session:
            stmt = (
                select(TrackNameRegistry)
                .where(TrackNameRegistry.user_id == user_id)
                .order_by(TrackNameRegistry.updated_at.desc())
            )
            result = await session.execute(stmt)
            if result:
                return result.scalars().all()
            return []

    async def set_user_track_names(
        self,
        user_id: int,
        track_part_name: str,
    ) -> None:
        """
        Сохраняет часть названия трека, связанную с пользователем.

        :param user_id: ID пользователя.
        :param track_part_name: Часть названия трека.
        """
        async with self.session_factory() as session:
            stmt = insert(TrackNameRegistry).values(
                user_id=user_id,
                track_part=track_part_name,
            )
            try:
                await session.execute(stmt)
            except Exception:  # noqa: BLE001
                await session.rollback()
            else:
                await session.commit()
