from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domains.users.repository import UserRepository
from src.domains.users.schemas import UsersSchema


@pytest.mark.asyncio
async def test_insert_new_user():
    session = AsyncMock()
    session_factory = MagicMock(return_value=session)
    repo = UserRepository(session_factory=session_factory)
    user_data = UsersSchema(id=1, username="test", first_name="Test", last_name="User")
    session.execute.return_value.scalars.return_value.first.return_value = 1
    await repo.insert_new_user(user_data)
    session.execute.assert_awaited()
    session.commit.assert_awaited()

@pytest.mark.asyncio
async def test_get_users():
    session = AsyncMock()
    session_factory = MagicMock(return_value=session)
    repo = UserRepository(session_factory=session_factory)
    session.execute.return_value.scalars.return_value.all.return_value = ["user1", "user2"]
    users = await repo.get_users()
    assert users == ["user1", "user2"]

@pytest.mark.asyncio
async def test_get_user_by_id():
    session = AsyncMock()
    session_factory = MagicMock(return_value=session)
    repo = UserRepository(session_factory=session_factory)
    session.execute.return_value.scalars.return_value.first.return_value = "user1"
    user = await repo.get_user_by_id(1)
    assert user == "user1"

@pytest.mark.asyncio
async def test_get_user_by_username():
    session = AsyncMock()
    session_factory = MagicMock(return_value=session)
    repo = UserRepository(session_factory=session_factory)
    session.execute.return_value.scalars.return_value.first.return_value = "user1"
    user = await repo.get_user_by_username("test")
    assert user == "user1"

@pytest.mark.asyncio
async def test_get_user_track_names():
    session = AsyncMock()
    session_factory = MagicMock(return_value=session)
    repo = UserRepository(session_factory=session_factory)
    session.execute.return_value.scalars.return_value.all.return_value = ["track1", "track2"]
    tracks = await repo.get_user_track_names(1)
    assert tracks == ["track1", "track2"]

@pytest.mark.asyncio
async def test_set_user_track_names():
    session = AsyncMock()
    session_factory = MagicMock(return_value=session)
    repo = UserRepository(session_factory=session_factory)
    await repo.set_user_track_names(1, "part")
    session.execute.assert_awaited()
    session.commit.assert_awaited()

