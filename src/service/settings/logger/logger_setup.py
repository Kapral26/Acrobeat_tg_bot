import logging.config
from pathlib import Path

import yaml

CONFIG_PATH = Path(__file__).parent / "config.yaml"

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def configure_logging(debug: bool = True):
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"standard": {"format": config["logging"]["format"]}},
        "handlers": {},
        "loggers": {},
        "root": {  # явное объявление root
            "handlers": ["console", "file_app"],
            "level": config["logging"]["level"],
        },
    }

    # handlers
    for name, handler in config["logging"]["handlers"].items():
        logging_config["handlers"][name] = {
            "class": handler["class"],
            "level": handler.get("level"),
            "formatter": "standard",
        }
        if "filename" in handler:
            logging_config["handlers"][name]["filename"] = handler["filename"]

    # loggers
    for logger_name, logger_conf in config["logging"]["loggers"].items():
        logging_config["loggers"][logger_name] = {
            "handlers": logger_conf["handlers"],
            "level": logger_conf.get("level"),
            "propagate": logger_conf.get("propagate", False),
        }

    logging.config.dictConfig(logging_config)

    if debug:
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        # дополнительно можно перевести в DEBUG критичные сервисные логгеры
        for logger_name in config["logging"]["loggers"].keys():
            logging.getLogger(logger_name).setLevel(logging.DEBUG)
