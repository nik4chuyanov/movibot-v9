from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Movibot MVP"
    env: str = "dev"
    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = Field(
        default="postgresql+psycopg://movibot:movibot@db:5432/movibot"
    )
    redis_url: str = "redis://redis:6379/0"

    scanner_interval_seconds: int = 60
    publish_interval_seconds: int = 20

    scanner_seed_sources: str = "https://example.com/feed"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
