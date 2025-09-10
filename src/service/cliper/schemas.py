from pydantic import BaseModel, \
    Field, \
    field_validator, \
    model_validator


class AudioMetadata(BaseModel):
    """DTO для метаданных аудиофайла."""

    duration: float = Field(..., gt=0, description="Длительность аудио в секундах")
    bitrate: int | None = Field(None, description="Битрейт аудио")
    sample_rate: int | None = Field(None, description="Частота дискретизации")


class AudioClipConfig(BaseModel):
    """Конфигурация для вырезки аудиофрагмента."""

    start_sec: float = Field(
        ...,
        ge=0,
        description="Время начала фрагмента в секундах",
    )
    finish_sec: float = Field(
        ...,
        gt=0,
        description="Длительность фрагмента в секундах",
    )
    output_format: str = Field("mp3", description="Формат выходного файла")

    @field_validator("output_format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        allowed = {"mp3", "wav", "flac", "ogg"}
        if v not in allowed:
            msg = f"Unsupported format: {v}. Allowed: {', '.join(allowed)}"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    @classmethod
    def validate_time_difference(cls, values) -> str:
        start = values.start_sec
        finish = values.finish_sec

        max_diff_seconds = 10
        if finish - start < max_diff_seconds:
            msg = "finish_sec не может быть меньше start_sec менее чем на 10 секунд"
            raise ValueError(msg)
        return values


class FadeConfig(BaseModel):
    """Конфигурация эффекта затухания."""

    fade_duration: float = Field(2.0, gt=0, description="Длительность затухания в секундах")
    fade_type: str = Field("out", description="Тип затухания: 'in' или 'out'")
