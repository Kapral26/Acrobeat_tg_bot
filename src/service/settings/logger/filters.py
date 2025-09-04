"""Модуль с классами фильтра для логгирования."""

import logging


class OwnLoggerFilter(logging.Filter):
    """
    Фильтр для логгирования, который позволяет пропускать сообщения только от определённых логгеров.

    Фильтр проверяет префиксы имен логгеров и разрешает запись сообщений только если имя логгера
    начинается с одного из указанных префиксов.
    """

    def __init__(self, allowed_loggers_prefixes: list[str]):
        """
        Инициализация фильтра.

        :param allowed_loggers_prefixes: Список строк — допустимые префиксы имен логгеров.
        """
        super().__init__()
        self.allowed_loggers_prefixes = allowed_loggers_prefixes

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Проверяет, соответствует ли имя логгера одному из допустимых префиксов.

        :param record: Объект лог-записи, переданный из логгера.
        :return: `True`, если имя логгера соответствует одному из допустимых префиксов, иначе `False`.
        """
        return any(record.name.startswith(prefix) for prefix in self.allowed_loggers_prefixes)
