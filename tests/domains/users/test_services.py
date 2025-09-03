from unittest.mock import AsyncMock

import pytest

from src.domains.users.schemas import UsersSchema
from src.domains.users.services import UserService, extract_user_data


class DummyEvent:
    class from_user:
        id = 1
        username = "test"
        first_name = "Test"
        last_name = "User"

@pytest.mark.asyncio
async def test_extract_user_data_decorator():
    called = {}
    @extract_user_data
    async def handler(self, event, user_data):
        called['user_data'] = user_data
        return user_data
    result = await handler(None, DummyEvent())
    assert isinstance(result, UsersSchema)
    assert result.id == 1
    assert result.username == "test"
    assert called['user_data'].first_name == "Test"

@pytest.mark.asyncio
async def test_user_service_register():
    repo = AsyncMock()
    cache = AsyncMock()
    service = UserService(user_repository=repo, user_cache_repository=cache)
    user_data = UsersSchema(id=1, username="test", first_name="Test", last_name="User")
    await service.register_user(user_data)
    repo.insert_new_user.assert_awaited_with(user_data)

