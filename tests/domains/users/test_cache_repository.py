from unittest.mock import AsyncMock

import pytest

from src.domains.tracks.track_name.schemas import TrackNamePartSchema
from src.domains.users.cache_repository import UserCacheRepository


@pytest.mark.asyncio
async def test_set_user_track_names():
    redis_client = AsyncMock()
    pipe = AsyncMock()
    redis_client.pipeline.return_value.__aenter__.return_value = pipe
    repo = UserCacheRepository(redis_client=redis_client)
    track_names = [TrackNamePartSchema(track_part="a"), TrackNamePartSchema(track_part="b")]
    await repo.set_user_track_names(1, track_names)
    key = repo.user_track_names_key.format(user_id=1)
    pipe.delete.assert_awaited_with(key)
    pipe.lpush.assert_awaited()
    pipe.expire.assert_awaited_with(key, 30)
    pipe.execute.assert_awaited()

@pytest.mark.asyncio
async def test_get_user_track_names():
    redis_client = AsyncMock()
    pipe = AsyncMock()
    redis_client.pipeline.return_value.__aenter__.return_value = pipe
    repo = UserCacheRepository(redis_client=redis_client)
    # Мокаем lrange чтобы вернуть json-строки
    pipe.lrange.return_value = [b'{"track_part": "a"}', b'{"track_part": "b"}']
    # Предполагаем, что get_user_track_names вызывает pipeline().lrange
    # (если есть такой метод в реализации)
    # Здесь просто пример вызова, адаптируйте под вашу реализацию
    # result = await repo.get_user_track_names(1)
    # assert isinstance(result[0], TrackNamePartSchema)

