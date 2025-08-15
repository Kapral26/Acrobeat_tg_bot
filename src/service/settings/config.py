import logging
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.service.settings.logger import setup_file_logger

dotenv_path = Path(__file__).parent.parent.parent.parent.absolute() / ".env"


class Settings(BaseSettings):
    """Класс настроек."""

    debug: bool = Field(..., alias="DEBUG")


    bot_token: SecretStr = Field(..., alias="BOT_TOKEN")

    postgres_user: str = Field(..., alias="POSTGRES_USER")
    postgres_password: SecretStr = Field(..., alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(..., alias="POSTGRES_DB")  # Название базы данных
    postgres_host: str = Field(..., alias="POSTGRES_HOST")  # Хост-сервера базы данных
    postgres_port: int = Field(..., alias="POSTGRES_PORT")  # Порт сервера базы данных

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        setup_file_logger(
            log_file="acrobeat_bot.log",
            log_level=logging.INFO if not self.debug else logging.DEBUG
        )

    @property
    def async_database_dsn(self) -> str:
        """Возвращает объект URL для подключения к PostgresSQL с использованием sqlalchemy и драйвера psycopg2."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password.get_secret_value()}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = SettingsConfigDict(env_file=dotenv_path, env_file_encoding="utf-8")


if __name__ == "__main__":
    settings = Settings()
    a = 1
