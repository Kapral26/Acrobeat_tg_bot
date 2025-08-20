import logging
from dataclasses import dataclass
from functools import wraps

from aiogram import types

from src.domains.tracks.track_name.schemas import TrackPartSchema
from src.domains.users.repository import UserRepository
from src.domains.users.schemas import UsersSchema


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
    logger: logging.Logger

    @extract_user_data
    async def register_user(
        self,
        event: types.TelegramObject,
        user_data: UsersSchema,
    ) -> None:
        if await self.user_repository.get_user_by_id(user_data.id):
            self.logger.info(f"User {user_data.id} already exists")
            return

        self.logger.info("Registering new user")
        await self.user_repository.insert_new_user(user_data)
        self.logger.info(f"New user registered: {user_data}")

    async def get_user_by_id(self, user_id: int) -> UsersSchema | None:
        user = await self.user_repository.get_user_by_id(user_id)
        if user is None:
            return None
        return UsersSchema.model_validate(user)

    async def get_user_tracks(self, user_id: int) -> list[TrackPartSchema] | None:
        user_tracks = await self.user_repository.get_user_tracks(user_id)
        if user_tracks is None:
            return None
        return [TrackPartSchema.model_validate(x) for x in user_tracks]
