import logging
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
