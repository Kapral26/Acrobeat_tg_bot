from pathlib import Path

from load_dotenv import load_dotenv
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

dotenv_path = Path(__file__).parent.parent.parent.parent.absolute() / ".env"
load_dotenv(dotenv_path.as_posix())


class PostgresSettings(BaseSettings):
    user: str = Field(validation_alias="POSTGRES_USER")
    password: SecretStr = Field(validation_alias="POSTGRES_PASSWORD")
    db: str = Field(validation_alias="POSTGRES_DB")
    host: str = Field(validation_alias="POSTGRES_HOST")
    port: int = Field(validation_alias="POSTGRES_PORT")

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
    aws_secret_access_key: str = Field(validation_alias="MINIO_AWS_SECRET_ACCESS_KEY")
    aws_access_key_id: str = Field(validation_alias="MINIO_AWS_ACCESS_KEY_ID")
    region_name: str = Field(validation_alias="MINIO_REGION_NAME")
    host: str = Field(validation_alias="MINIO_HOST")
    port: int = Field(validation_alias="MINIO_PORT")

    @property
    def endpoint_url(self) -> str:
        return f"{self.host}:{self.port}"


    class Config:
        env_prefix = "MINIO_"


class RedisSettings(BaseSettings):
    host: str = Field(validation_alias="REDIS_HOST")
    port: int = Field(validation_alias="REDIS_PORT")
    db: int = Field(validation_alias="REDIS_DB")

    class Config:
        env_prefix = "REDIS_"


class BotSettings(BaseSettings):
    token: SecretStr = Field(validation_alias="BOT_TOKEN")

    class Config:
        env_prefix = "BOT_"


class Settings(BaseSettings):
    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    minio: MinIOSettings = Field(default_factory=MinIOSettings)
    bot: BotSettings = Field(default_factory=BotSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    debug: bool = Field(validation_alias="DEBUG", default=False)


    model_config = {
        "env_nested_delimiter": "__",
        "case_insensitive": True,
    }


if __name__ == "__main__":
    settings = Settings()
