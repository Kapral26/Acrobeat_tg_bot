import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.users.models import User
from src.domains.users.schemas import UsersSchema


@dataclass
class UserRepository:
    session_factory: Callable[[], AsyncSession]
    logger: logging.Logger


    async def insert_new_user(
            self,
        session: AsyncSession,
            user_data: UsersSchema
    ) -> int:
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

        query_result.scalars().first()

    async def get_users(self) -> Sequence[User]:
        async with self.session_factory() as session:
            query_result = await session.execute(
                select(User)
            )
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
            stmt = (
                select(User)
                .where(User.username == username)
            )
            result = await session.execute(stmt)
            return result.scalars().first()
