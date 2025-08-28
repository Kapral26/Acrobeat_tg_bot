from pydantic import BaseModel, computed_field, field_validator

from src.domains.tracks.track_cliper.utils import (
    calculate_clip_duration,
    is_valid_time_format,
)


class ClipPeriodSchema(BaseModel):
    start: str
    finish: str

    @field_validator("start", "finish")
    def check_time_format(cls, v: str) -> str:
        if not is_valid_time_format(v):
            raise ValueError(
                f"Неверный формат времени '{v}'. Используйте формат 'mm:ss'"
            )
        return v

    @computed_field
    @property
    def duration_sec(self) -> int:
        return calculate_clip_duration(self.start, self.finish)

    @computed_field
    @property
    def start_sec(self) -> float:
        return float(
            ".".join(self.start.split(":"))
        )

if __name__ == "__main__":
    data = {"start": "01:30", "finish": "02:45"}
    clip = ClipPeriodSchema.model_validate(data)
    a = 1