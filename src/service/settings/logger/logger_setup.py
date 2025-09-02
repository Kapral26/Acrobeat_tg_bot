"""
Модуль `logger_setup.py` отвечает за настройку логгирования приложения.

Конфигурация логгирования загружается из YAML-файла и применяется через `logging.config.dictConfig`.
"""

import logging.config
from pathlib import Path

import yaml

# Путь к конфигурационному файлу логгирования
CONFIG_PATH = Path(__file__).parent / "config.yaml"

# Директория для хранения лог-файлов
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def configure_logging(debug: bool = True) -> None:
    """
    Настраивает логгирование приложения на основе конфигурации из файла.

    Загружает настройки из `config.yaml`, формирует словарь конфигурации для `dictConfig`
    и применяет его. Также может включать отладочное логгирование, если `debug=True`.

    :param debug: Если `True`, уровень логгирования устанавливается в DEBUG.
    """
    # Загрузка базовой конфигурации из YAML
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"standard": {"format": config["logging"]["format"]}},
        "handlers": {},
        "loggers": {},
        "root": {  # явное объявление root logger
            "handlers": ["console", "file_app"],
            "level": config["logging"]["level"],
        },
    }

    # Добавление обработчиков (handlers)
    for name, handler in config["logging"]["handlers"].items():
        logging_config["handlers"][name] = {
            "class": handler["class"],
            "level": handler.get("level"),
            "formatter": "standard",
        }
        if "filename" in handler:
            logging_config["handlers"][name]["filename"] = handler["filename"]

    # Добавление логгеров (loggers)
    for logger_name, logger_conf in config["logging"]["loggers"].items():
        logging_config["loggers"][logger_name] = {
            "handlers": logger_conf["handlers"],
            "level": logger_conf.get("level"),
            "propagate": logger_conf.get("propagate", False),
        }

    # Применение конфигурации
    logging.config.dictConfig(logging_config)

    # Включение отладочной информации, если требуется
    if debug:
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        # Установка уровня DEBUG для указанных логгеров
        for logger_name in config["logging"]["loggers"].keys():
            logging.getLogger(logger_name).setLevel(logging.DEBUG)