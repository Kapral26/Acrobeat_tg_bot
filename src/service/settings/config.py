import logging
from pathlib import Path

from load_dotenv import load_dotenv
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

from src.service.settings.logger import setup_file_logger

dotenv_path = Path(__file__).parent.parent.parent.parent.absolute() / ".env"
load_dotenv(dotenv_path.as_posix())


class PostgresSettings(BaseSettings):
    user: str = Field(..., env="POSTGRES_USER")
    password: SecretStr = Field(..., env="POSTGRES_PASSWORD")
    db: str = Field(..., env="POSTGRES_DB")
    host: str = Field(..., env="POSTGRES_HOST")
    port: int = Field(..., env="POSTGRES_PORT")

    @property
    def async_database_dsn(self) -> str:
        """Возвращает объект URL для подключения к PostgresSQL с использованием sqlalchemy и драйвера psycopg2."""
        return (
            f"postgresql+asyncpg://{self.user}:"
            f"{self.password.get_secret_value()}@"
            f"{self.host}:{self.port}/{self.db}"
        )

    class Config:
        env_prefix = "POSTGRES_"


class MinIOSettings(BaseSettings):
    root_user: str = Field(..., env="MINIO_ROOT_USER")
    root_password: str = Field(..., env="MINIO_ROOT_PASSWORD")

    class Config:
        env_prefix = "MINIO_"


class BotSettings(BaseSettings):
    token: SecretStr = Field(..., env="BOT_TOKEN")

    class Config:
        env_prefix = "BOT_"


audio_path = Path(__file__).parent.parent.absolute() / "audio"  # TODO Удалить


class Settings(BaseSettings):
    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    minio: MinIOSettings = Field(default_factory=MinIOSettings)
    bot: BotSettings = Field(default_factory=BotSettings)
    debug: bool = Field(..., env="DEBUG")
    path_audio: Path = audio_path

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        setup_file_logger(
            log_file="acrobeat_bot.log",
            log_level=logging.INFO if not self.debug else logging.DEBUG,
        )

    model_config = {
        "env_nested_delimiter": "__",
        "case_insensitive": True,
    }


if __name__ == "__main__":
    settings = Settings()
