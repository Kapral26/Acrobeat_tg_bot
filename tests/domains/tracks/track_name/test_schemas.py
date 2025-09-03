from src.domains.tracks.track_name.schemas import TrackNamePartSchema


def test_track_name_part_schema_create():
    schema = TrackNamePartSchema(id=1, track_part="TestPart")
    assert schema.id == 1
    assert schema.track_part == "TestPart"
    # Проверка сериализации
    data = schema.model_dump()
    assert data["id"] == 1
    assert data["track_part"] == "TestPart"

