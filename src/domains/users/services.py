import logging
from dataclasses import dataclass
from functools import wraps

from aiogram import types

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
        self.logger.info("Registering new user")
        await self.user_repository.insert_new_user(user_data)
        self.logger.info(f"New user registered: {user_data}")

    async def get_user_by_id(self, user_id: int) -> UsersSchema:
        user = await self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User not found") # TODO Реализовать исключение под эту проблему.
        return UsersSchema.model_validate(user)
