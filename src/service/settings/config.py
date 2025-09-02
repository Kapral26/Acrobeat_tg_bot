"""
Модуль `config.py` отвечает за настройку и загрузку конфигурации приложения.

Использует Pydantic для валидации и автоматического получения значений из переменных окружения.
"""

from pathlib import Path

from load_dotenv import load_dotenv
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

# Путь к файлу .env, который будет использоваться для загрузки переменных окружения
dotenv_path = Path(__file__).parent.parent.parent.parent.absolute() / ".env"
load_dotenv(dotenv_path.as_posix())


class PostgresSettings(BaseSettings):
    """Класс для хранения настроек подключения к PostgreSQL."""

    user: str = Field(validation_alias="POSTGRES_USER")
    password: SecretStr = Field(validation_alias="POSTGRES_PASSWORD")
    db: str = Field(validation_alias="POSTGRES_DB")
    host: str = Field(validation_alias="POSTGRES_HOST")
    port: int = Field(validation_alias="POSTGRES_PORT")

    @property
    def async_database_dsn(self) -> str:
        """
        Возвращает DSN (Data Source Name) для асинхронного подключения к PostgreSQL через SQLAlchemy.

        Формат: postgresql+asyncpg://<user>:<password>@<host>:<port>/<db>

        :return: Строка DSN.
        """
        return (
            f"postgresql+asyncpg://{self.user}:"
            f"{self.password.get_secret_value()}@"
            f"{self.host}:{self.port}/{self.db}"
        )

    class Config:
        """Настройки Pydantic для класса PostgresSettings."""

        env_prefix = "POSTGRES_"


class RedisSettings(BaseSettings):
    """Класс для хранения настроек подключения к Redis."""

    host: str = Field(validation_alias="REDIS_HOST")
    port: int = Field(validation_alias="REDIS_PORT")
    db: int = Field(validation_alias="REDIS_DB")

    class Config:
        """Настройки Pydantic для класса RedisSettings."""

        env_prefix = "REDIS_"


class BotSettings(BaseSettings):
    """Класс для хранения настроек телеграм-бота."""

    token: SecretStr = Field(validation_alias="BOT_TOKEN")

    class Config:
        """Настройки Pydantic для класса BotSettings."""

        env_prefix = "BOT_"


class Settings(BaseSettings):
    """Основной класс конфигурации приложения. Объединяет все остальные настройки."""

    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    bot: BotSettings = Field(default_factory=BotSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    debug: bool = Field(validation_alias="DEBUG", default=False)

    model_config = {
        "env_nested_delimiter": "__",  # Разделитель для вложенных переменных окружения
        "case_insensitive": True,       # Игнорирование регистра при чтении переменных окружения
    }


if __name__ == "__main__":
    """
    Точка входа для тестирования модуля.
    При запуске файла как скрипта создаёт экземпляр Settings и выводит его содержимое.
    """
    settings = Settings()