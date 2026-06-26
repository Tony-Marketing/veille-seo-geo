"""Configuration applicative."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Veille SEO-GEO Groupe A.P&Partner"
    app_version: str = "0.6.0"
    environment: str = "development"
    debug: bool = False
    database_url: str = "sqlite:///./veille_seo_geo.db"
    secret_key: str = Field(default="change-me-in-env", min_length=8)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    api_key_encryption_secret: str | None = None
    exports_directory: str = "exports"
    backups_directory: str = "backups"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()


settings = get_settings()
