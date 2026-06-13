from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BASE_DIR.parent / ".env"


class Settings(BaseSettings):
    # Базовые настройки приложения и окружения.
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    DATABASE_URL: str = Field(
        default="sqlite:///./sppr.db",
        description="URL подключения к базе данных.",
    )
    DEBUG: bool = Field(
        default=False,
        description="Режим отладки приложения.",
    )
    API_PREFIX: str = Field(
        default="/api",
        description="Префикс для API-маршрутов.",
    )
    PROJECT_NAME: str = Field(
        default="SPPR PersFin",
        description="Название проекта.",
    )


settings = Settings()
