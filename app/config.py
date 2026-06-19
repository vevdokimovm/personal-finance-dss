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
        default="3.1.0",
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


    # ── v3.0.0 International: auth (INFRA-06, NFR-05) ──────────────────
    JWT_SECRET: str = Field(
        default="dev-insecure-secret-change-me-in-production-env-32b",
        description="Секрет подписи JWT. В продакшне ОБЯЗАТЕЛЬНО задать в .env.",
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="Алгоритм подписи JWT.")
    JWT_TTL_HOURS: int = Field(default=168, description="Срок жизни access-токена, часов.")
    AUTH_COOKIE_NAME: str = Field(default="fp_access", description="Имя httpOnly-cookie с JWT.")
    COOKIE_SECURE: bool = Field(
        default=False,
        description=(
            "Ставить ли флаг Secure на auth-cookie. False (по умолчанию) — кука "
            "работает по HTTP (локально/Docker). True — только когда фронт реально "
            "обслуживается по HTTPS, иначе браузер не пришлёт куку и вход сломается."
        ),
    )

    # ── v3.0.0 International: мультивалюта (FR-19, DATA-08) ────────────
    DEFAULT_BASE_CURRENCY: str = Field(
        default="RUB",
        description="Базовая валюта по умолчанию для новых пользователей.",
    )

    # ── v3.0.0 International: B2B /v1/analyze (FR-23) ──────────────────
    B2B_API_KEYS: str = Field(
        default="",
        description="API-ключи партнёров через запятую. Пусто = эндпоинт отключён.",
    )

    # ── v3.0.0 International: Plaid (FR-18, INFRA-16, INFRA-17) ────────
    PLAID_CLIENT_ID: str = Field(default="", description="Plaid client_id (sandbox/prod).")
    PLAID_SECRET: str = Field(default="", description="Plaid secret. Только через .env.")
    PLAID_ENV: str = Field(default="sandbox", description="Окружение Plaid: sandbox | production.")
    TOKEN_ENCRYPTION_KEY: str = Field(
        default="",
        description="Fernet-ключ шифрования Plaid-токенов (INFRA-17). Пусто = derive из JWT_SECRET.",
    )

    @property
    def b2b_api_keys_list(self) -> list[str]:
        return [k.strip() for k in self.B2B_API_KEYS.split(",") if k.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.strip().lower() == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # ── Email (приветственное письмо при регистрации) ──────────────────
    # Пусто = почта выключена, регистрация работает без отправки (graceful).
    SMTP_HOST: str = Field(default="", description="SMTP-сервер. Пусто = почта отключена.")
    SMTP_PORT: int = Field(default=587, description="Порт SMTP (587 STARTTLS / 465 SSL).")
    SMTP_USER: str = Field(default="", description="Логин SMTP.")
    SMTP_PASSWORD: str = Field(default="", description="Пароль/токен SMTP.")
    SMTP_FROM: str = Field(default="", description="Адрес отправителя. Пусто = SMTP_USER.")
    SMTP_USE_TLS: bool = Field(default=True, description="STARTTLS (True) или SSL (False).")

    @property
    def email_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.SMTP_USER and self.SMTP_PASSWORD)


settings = Settings()
