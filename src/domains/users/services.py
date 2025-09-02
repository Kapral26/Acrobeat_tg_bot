import logging
from dataclasses import dataclass
from functools import wraps

from aiogram import types

from src.domains.tracks.track_name.schemas import TrackNamePartSchema
from src.domains.users.cache_repository import UserCacheRepository
from src.domains.users.repository import UserRepository
from src.domains.users.schemas import UsersSchema

logger = logging.getLogger(__name__)


def extract_user_data(func):
    @wraps(func)
    async def wrapper(self, event: types.TelegramObject, *args, **kwargs):
        # Общий метод извлечения данных пользователя
        user = event.from_user

        user_data = UsersSchema(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        return await func(self, event, user_data, *args, **kwargs)

    return wrapper


@dataclass
class UserService:
    user_repository: UserRepository
    user_cache_repository: UserCacheRepository
    user_session_track_name: str = "session_track_name:{user_id}"
    user_session_query_text: str = "session_query_text:{user_id}"

    @extract_user_data
    async def register_user(
        self,
        event: types.TelegramObject,  # noqa: unused
        user_data: UsersSchema,
    ) -> None:
        if await self.user_repository.get_user_by_id(user_data.id):
            logger.info(f"User {user_data.id} already exists")
            return

        logger.info("Registering new user")
        await self.user_repository.insert_new_user(user_data)
        logger.info(f"New user registered: {user_data}")

    async def get_user_by_id(self, user_id: int) -> UsersSchema | None:
        user = await self.user_repository.get_user_by_id(user_id)
        if user is None:
            return None
        return UsersSchema.model_validate(user)

    async def get_user_track_names(
        self, user_id: int
    ) -> list[TrackNamePartSchema] | None:
        if user_tracks := await self.user_cache_repository.get_user_track_names(
            user_id
        ):
            pass
        else:
            user_tracks = await self.user_repository.get_user_track_names(user_id)
            if user_tracks:
                user_tracks = [
                    TrackNamePartSchema.model_validate(x) for x in user_tracks
                ]
                await self.user_cache_repository.set_user_track_names(
                    user_id=user_id, track_names=user_tracks
                )
        return user_tracks

    async def set_user_track_names(
        self, user_id: int, second_name: str, first_name: str, year_of_birth: int
    ):
        track_part_name = f"{second_name}_{first_name}_{year_of_birth}"
        await self.user_repository.set_user_track_names(user_id, track_part_name)

    async def set_session_track_names(self, user_id: int, track_name: str):
        key = self.user_session_track_name.format(user_id=user_id)
        await self.user_cache_repository.set(key, track_name, 180)

    async def get_session_track_name(self, user_id: int) -> str:
        key = self.user_session_track_name.format(user_id=user_id)
        session_track_name = await self.user_cache_repository.get(key)

        if not session_track_name:
            logger.warning("Session track does not exist")

        return session_track_name

    async def del_session_track_name(self, user_id: int) -> None:
        key = self.user_session_track_name.format(user_id=user_id)
        session_track_name = await self.user_cache_repository.delete(key)

        if not session_track_name:
            logger.warning("Session track does not exist")

    async def set_session_query_text(self, user_id: int, query_text: str):
        key = self.user_session_query_text.format(user_id=user_id)
        await self.user_cache_repository.set(key, query_text, ttl=180)

    async def get_session_query_text(self, user_id: int) -> str:
        key = self.user_session_query_text.format(user_id=user_id)
        session_user_query = await self.user_cache_repository.get(key)

        if not session_user_query:
            logger.warning("Session query text does not exist")

        return session_user_query

    async def del_session_query_text(self, user_id: int) -> None:
        key = self.user_session_query_text.format(user_id=user_id)
        session_user_query = await self.user_cache_repository.delete(key)

        if not session_user_query:
            logger.warning("Session query text does not exist")

    async def get_and_del_session_query_text(self, user_id: int) -> str:
        session_query_text = await self.get_session_query_text(user_id)
        await self.del_session_query_text(user_id)
        return session_query_text
