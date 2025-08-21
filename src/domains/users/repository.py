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
    session_factory: Callable[[], AsyncSession]

    async def insert_new_user(self, user_data: UsersSchema):
        async with self.session_factory() as session:
            stmnt = (
                insert(User)
                .values(
                    id=user_data.id,
                    username=user_data.username,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name,
                )
                .returning(User.id)
            )
            try:
                query_result = await session.execute(stmnt)
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()

        query_result.scalars().first()

    async def get_users(self) -> Sequence[User]:
        async with self.session_factory() as session:
            query_result = await session.execute(select(User))
            return query_result.scalars().all()

    async def get_user_by_id(self, user_id: int) -> User | None:
        async with self.session_factory() as session:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_user_by_username(self, username: str) -> User | None:
        async with self.session_factory() as session:
            # Сбрасываем кэш SQLAlchemy
            session.expire_all()
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_user_track_names(
        self, user_id: int
    ) -> Sequence[TrackNameRegistry] | list[Any]:
        async with self.session_factory() as session:
            stmnt = (
                select(TrackNameRegistry)
                .where(TrackNameRegistry.user_id == user_id)
                .order_by(TrackNameRegistry.updated_at.desc())
            )
            result = await session.execute(stmnt)
            if result:
                return result.scalars().all()
            return []

    async def set_user_track_names(self, user_id: int, track_part_name: str):
        async with self.session_factory() as session:
            stmnt = insert(TrackNameRegistry).values(
                user_id=user_id,
                track_part=track_part_name,
            )
            try:
                await session.execute(stmnt)
            except Exception as e:
                await session.rollback()
            else:
                await session.commit()
