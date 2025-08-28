import re


def is_valid_time_format(time_str: str) -> bool:
    """
    Проверяет, что строка соответствует формату '00:00'.
    """
    time_pattern = r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
    return re.match(time_pattern, time_str.strip()) is not None


def calculate_clip_duration(start_time: str, end_time: str) -> int:
    """
    Рассчитывает разницу между двумя временными метками в формате 'mm:ss'.
    Возвращает разницу в секундах.

    :param start_time: Время начала в формате 'mm:ss'
    :param end_time: Время окончания в формате 'mm:ss'
    :return: Разница в секундах
    """
    def time_to_seconds(time_str: str) -> int:
        minutes, seconds = map(int, time_str.split(":"))
        return minutes * 60 + seconds

    start_sec = time_to_seconds(start_time)
    end_sec = time_to_seconds(end_time)

    if end_sec < start_sec:
        raise ValueError("Время окончания не может быть меньше времени начала")

    return end_sec - start_sec
