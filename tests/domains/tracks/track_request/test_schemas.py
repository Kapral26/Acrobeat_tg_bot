"""
Тесты для TrackRequestSchema:
- Проверка создания и сериализации схемы запроса трека.
"""

from src.domains.tracks.track_request.schemas import TrackRequestSchema


def test_track_request_schema_create() -> None:
    """
    Проверяет создание и сериализацию TrackRequestSchema.
    """
    schema = TrackRequestSchema(user_id=1, query_text="test query")
    assert schema.user_id == 1
    assert schema.query_text == "test query"
    data = schema.model_dump()
    assert data["user_id"] == 1
    assert data["query_text"] == "test query"
