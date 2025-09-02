"""
Модуль `utils.py` содержит вспомогательные функции для работы с временными метками и расчётом длительности аудиообрезки.

Обеспечивает:
- проверку корректности формата временных строк;
- вычисление разницы между двумя временными метками в секундах.
"""

import re


def is_valid_time_format(time_str: str) -> bool:
    """
    Проверяет, соответствует ли строка формату времени 'HH:MM'.

    Используется регулярное выражение для валидации строки:
    - часы: 00–23 (с учётом ведущего нуля),
    - минуты: 00–59.

    :param time_str: Временная строка в формате 'HH:MM'.
    :return: `True`, если формат корректен, иначе `False`.

    Примеры:
        >>> is_valid_time_format("14:30")
        True
        >>> is_valid_time_format("23:59")
        True
        >>> is_valid_time_format("24:00")
        False
    """
    time_pattern = r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
    return re.match(time_pattern, time_str.strip()) is not None


def calculate_clip_duration(start_time: str, end_time: str) -> int:
    """
    Рассчитывает разницу между двумя временными метками в формате 'mm:ss' в секундах.

    Предполагается, что входные строки представляют время в минутах и секундах.
    Если время окончания меньше времени начала, выбрасывается исключение.

    :param start_time: Время начала в формате 'mm:ss'.
    :param end_time: Время окончания в формате 'mm:ss'.
    :return: Разница между временем окончания и началом в секундах.
    :raises ValueError: Если время окончания меньше времени начала.

    Примеры:
        >>> calculate_clip_duration("01:15", "02:30")
        75
        >>> calculate_clip_duration("10:00", "09:59")
        Traceback (most recent call last):
        ...
        ValueError: Время окончания не может быть меньше времени начала
    """

    def time_to_seconds(time_str: str) -> int:
        minutes, seconds = map(int, time_str.split(":"))
        return minutes * 60 + seconds

    start_sec = time_to_seconds(start_time)
    end_sec = time_to_seconds(end_time)

    if end_sec < start_sec:
        raise ValueError("Время окончания не может быть меньше времени начала")

    return end_sec - start_sec
