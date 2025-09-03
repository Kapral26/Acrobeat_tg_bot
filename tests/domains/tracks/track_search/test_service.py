"""
Тесты для TrackSearchService (поиск треков):
- Проверка вызова сервисов поиска и запросов треков.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domains.tracks.track_search.service import TrackSearchService


@pytest.mark.asyncio
async def test_search_tracks_calls_services() -> None:
    """
    Проверяет, что метод search_tracks вызывает методы downloader_service или track_request_service
    и не выбрасывает исключений при стандартном сценарии.
    """
    callback = MagicMock()
    bot = AsyncMock()
    downloader_service = AsyncMock()
    track_request_service = AsyncMock()
    state = AsyncMock()
    query_text = "test query"

    service = TrackSearchService()
    # Проверяем, что метод search_tracks не вызывает исключений и обращается к сервисам
    await service.search_tracks(
        callback=callback,
        bot=bot,
        downloader_service=downloader_service,
        track_request_service=track_request_service,
        state=state,
        query_text=query_text,
    )
    # downloader_service и track_request_service должны быть вызваны хотя бы раз
    assert downloader_service.method_calls or track_request_service.method_calls
