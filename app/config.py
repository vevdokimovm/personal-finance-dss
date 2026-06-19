from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BASE_DIR.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    DATABASE_URL: str = Field(
        default="sqlite:///./finpilot.db",
        description="URL подключения к базе данных.",
    )
    DEBUG: bool = Field(default=False, description="Режим отладки приложения.")
    API_PREFIX: str = Field(default="/api", description="Префикс для API-маршрутов.")
    PROJECT_NAME: str = Field(
        default="FINPILOT",
        description="Название проекта.",
    )
    APP_VERSION: str = Field(
        default="2.2.0",
        description="Версия приложения (INFRA-13): код, UI-футер, git-тег.",
    )
    PROJECT_TAGLINE: str = Field(
        default="Система поддержки принятия решений в персональных финансах",
        description="Подзаголовок продукта.",
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Окружение: development | production (INFRA-10/12).",
    )
    CORS_ORIGINS: str = Field(
        default="http://localhost:8000,http://127.0.0.1:8000",
        description="Разрешённые источники CORS через запятую (INFRA-12).",
    )
    RATE_LIMIT_REQUESTS: int = Field(
        default=30,
        description="Лимит запросов на чувствительные эндпоинты за окно (INFRA-12).",
    )
    RATE_LIMIT_WINDOW_SECONDS: int = Field(
        default=60,
        description="Размер окна rate-limit в секундах (INFRA-12).",
    )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.strip().lower() == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
