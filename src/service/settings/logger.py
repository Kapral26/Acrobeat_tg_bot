import logging
from collections.abc import Callable
from functools import wraps
from pathlib import Path


def setup_file_logger(
    log_file: str,
    log_level: int = logging.INFO,
    logger_name: str | None = None,
) -> logging.Logger:

    if not logger_name:
        logger_name = Path(log_file).stem

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # Не добавлять повторно хендлеры
    if not logger.handlers:
        log_dir = Path(__file__).parent.parent.parent.absolute()
        handler = logging.FileHandler(log_dir / log_file, encoding="utf-8")
        formatter = logging.Formatter(
            fmt="%(asctime)s| %(levelname)s | %(pathname)s | %(funcName)s | %(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_function(level: int = logging.INFO, logger_name: str = "app_logger"):
    """
    Декоратор для логирования вызовов обычных функций (не методов класса).
    Логирует вход, выход и ошибки функции.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name)
            logger.log(
                level,
                f"Вызов функции {func.__qualname__} с args={args}, kwargs={kwargs}",
            )
            try:
                result = func(*args, **kwargs)
                logger.log(
                    level,
                    f"Функция {func.__qualname__} успешно завершена, результат: {result!r}",
                )

            except Exception as e:
                logger.exception(f"Ошибка в функции {func.__qualname__}: {e}")
                raise

        return wrapper

    return decorator
