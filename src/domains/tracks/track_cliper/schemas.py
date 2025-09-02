"""
Модуль `schemas.py` содержит Pydantic-модель для описания временных параметров обрезки аудиофайлов.

Определяет схему `ClipPeriodSchema`, которая используется для валидации временных меток и расчёта длительности аудиообрезки.
"""

from pydantic import BaseModel, computed_field, field_validator

from src.domains.tracks.track_cliper.utils import (
    calculate_clip_duration,
    is_valid_time_format,
)


class ClipPeriodSchema(BaseModel):
    """
    Модель данных для хранения временных параметров обрезки трека.

    Используется для:
    - валидации формата временных меток (`mm:ss`);
    - расчёта продолжительности обрезки в секундах;
    - преобразования временных меток в числовые значения для дальнейшей обработки.
    """

    start: str
    finish: str

    @field_validator("start", "finish")
    def check_time_format(self, v: str) -> str:
        """
        Валидирует формат временной метки.

        Проверяет, соответствует ли строка формату `mm:ss`.
        Если формат некорректен, выбрасывает исключение `ValueError`.

        :param v: Временная метка в виде строки.
        :return: Строка валидного формата.
        :raises ValueError: Если формат не соответствует `mm:ss`.
        """
        if not is_valid_time_format(v):
            raise ValueError(
                f"Неверный формат времени '{v}'. Используйте формат 'mm:ss'"
            )
        return v

    @computed_field
    @property
    def duration_sec(self) -> int:
        """
        Вычисляет продолжительность обрезки в секундах.

        Использует утилиту `calculate_clip_duration` для определения разницы между временными метками.

        :return: Целое число, представляющее количество секунд между `start` и `finish`.
        """
        return calculate_clip_duration(self.start, self.finish)

    @computed_field
    @property
    def start_sec(self) -> float:
        """
        Преобразует временную метку `start` в десятичное число.

        Формат преобразования: `mm:ss` → `m.m`, где `m` — минуты, `s` — секунды.
        Например, `"01:30"` преобразуется в `1.3`.

        :return: Число с плавающей точкой, представляющее начальное время.
        """
        return float(".".join(self.start.split(":")))
