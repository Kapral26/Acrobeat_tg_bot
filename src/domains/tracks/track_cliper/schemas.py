"""
Модуль `schemas.py` содержит Pydantic-модель для описания временных
 параметров обрезки аудиофайлов.

Определяет схему `ClipPeriodSchema`, которая используется для валидации
 временных меток и расчёта длительности аудиообрезки.
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
    def check_time_format(cls, v: str) -> str:  # noqa: N805
        """
        Валидирует формат временной метки.

        Проверяет, соответствует ли строка формату `mm:ss`.
        Если формат некорректен, выбрасывает исключение `ValueError`.

        :param v: Временная метка в виде строки.
        :return: Строка валидного формата.
        :raises ValueError: Если формат не соответствует `mm:ss`.
        """
        if not is_valid_time_format(v):
            msg = f"Неверный формат времени '{v}'. Используйте формат 'mm:ss'"
            raise ValueError(msg)
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
    def start_sec(self) -> int:
        """
        Преобразует временную метку `start` в секунды

        Формат преобразования: `mm:ss` → `m.m`, где `m` — минуты, `s` — секунды.
        Например, `"01:30"` преобразуется в `90`.

        :return: Число с плавающей точкой, представляющее начальное время.
        """
        return self.time_marker_to_seconds(self.start)

    @computed_field
    @property
    def finish_sec(self) -> int:
        """
        Преобразует временную метку `finish` в секунды

        Формат преобразования: `mm:ss` → `m.m`, где `m` — минуты, `s` — секунды.
        Например, `"01:30"` преобразуется в `90`.

        :return: Число с плавающей точкой, представляющее начальное время.
        """
        return self.time_marker_to_seconds(self.finish)

    @staticmethod
    def time_marker_to_seconds(time_marker: str) -> int:
        """
        Преобразует временную метку из формата `mm:ss` в миллисекунды.
        :param time_marker: Временная метка в формате `mm:ss`.
        :return: Временная метка в миллисекундах.
        """
        minutes, second = (int(x) for x in time_marker.split(":"))
        return (minutes * 60 + second) * 1000
