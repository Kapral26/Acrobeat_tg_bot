from unittest.mock import MagicMock

import pytest

from src.service.downloader.service import DownloaderService


class DummyRepo:
    def __init__(self, alias):
        self.alias = alias

@pytest.mark.asyncio
async def test_get_repo_found():
    repo1 = DummyRepo("yt")
    repo2 = DummyRepo("vk")
    service = DownloaderService(
        external_repository=[repo1, repo2],
        cache_repository=MagicMock(),
        settings=MagicMock(),
    )
    assert service._get_repo("vk") is repo2

@pytest.mark.asyncio
async def test_get_repo_not_found():
    repo1 = DummyRepo("yt")
    service = DownloaderService(
        external_repository=[repo1],
        cache_repository=MagicMock(),
        settings=MagicMock(),
    )
    with pytest.raises(StopIteration):
        service._get_repo("not_exist")

