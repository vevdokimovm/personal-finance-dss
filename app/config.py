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
        default="4.16.36",
        description="Версия приложения (INFRA-13): код, UI-футер, git-тег.",
    )
    PROJECT_TAGLINE: str = Field(
        default="Система поддержки принятия решений в персональных финансах",
        description="Подзаголовок продукта.",
    )
    CBR_KEY_RATE_FALLBACK: float = Field(
        default=0.16,
        ge=0.0,
        le=1.0,
        description="Резервная ключевая ставка ЦБ (доля), если cbr.ru недоступен.",
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
    ADMIN_API_KEY: str = Field(
        default="",
        description="Ключ доступа к админ-эндпоинтам (аналитика, cron-триггеры). "
        "В продакшне ОБЯЗАТЕЛЕН; в dev пусто = эндпоинты открыты для удобства разработки (P3.4).",
    )
    PASSWORD_RESET_TTL_HOURS: int = Field(
        default=1, ge=1, description="Срок жизни токена сброса пароля, часов (P1.3)."
    )

    # ── Наблюдаемость (P1.5) ──────────────────────────────────────────
    SENTRY_DSN: str = Field(default="", description="DSN Sentry. Пусто = трекинг ошибок отключён.")
    LOG_LEVEL: str = Field(default="INFO", description="Уровень логирования (DEBUG/INFO/WARNING).")
    LOG_JSON: bool = Field(
        default=True,
        description="JSON-логи (True, для прода/агрегации) или человекочитаемый текст (False).",
    )

    # ── Импорт выписок (P2.1) ─────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = Field(
        default=10, ge=1, description="Максимальный размер загружаемого файла выписки, МБ."
    )
    AUTH_COOKIE_NAME: str = Field(default="fp_access", description="Имя httpOnly-cookie с JWT.")

    # ── Account lockout: защита логина от перебора (P1.2, NFR-05) ──────
    LOGIN_MAX_ATTEMPTS: int = Field(
        default=5,
        ge=1,
        description="Число неудачных попыток входа до временной блокировки аккаунта.",
    )
    LOGIN_LOCKOUT_MINUTES: int = Field(
        default=15,
        ge=1,
        description="Длительность блокировки аккаунта после превышения лимита, минут.",
    )
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

    # ── Юридические реквизиты оператора (P1.1, 152-ФЗ) ─────────────────
    # Подставляются в опубликованные документы и footer из единого места.
    # ИНН и адрес по умолчанию пусты: их нельзя выдумывать — это реальные
    # регистрационные данные. Пока не заполнены и флаг ниже не выставлен,
    # на юр-страницах показывается баннер «документ в стадии оформления».
    LEGAL_OPERATOR_NAME: str = Field(
        default="ООО «ФИНПАЙЛОТ»",
        description="Наименование оператора ПДн (юрлицо/ИП). До регистрации — заглушка.",
    )
    LEGAL_OPERATOR_INN: str = Field(
        default="",
        description="ИНН оператора. Пусто = не заполнено (фейковый ИНН недопустим).",
    )
    LEGAL_OPERATOR_ADDRESS: str = Field(
        default="",
        description="Юридический адрес оператора. Пусто = не заполнено.",
    )
    LEGAL_CONTACT_EMAIL: str = Field(
        default="support@finpilot.app",
        description="Контактный e-mail для обращений (в т.ч. по ПДн). Домен — заглушка.",
    )
    LEGAL_DOC_DATE: str = Field(
        default="",
        description="Дата вступления документов в силу (YYYY-MM-DD). Пусто = не указана.",
    )
    LEGAL_DATA_RETENTION_MONTHS: int = Field(
        default=6,
        ge=0,
        description="Срок хранения данных после удаления учётной записи, месяцев.",
    )
    LEGAL_DETAILS_CONFIRMED: bool = Field(
        default=False,
        description=(
            "Подтверждение, что реквизиты внесены и проверены (юрлицо зарегистрировано, "
            "документы прошли юр-ревью). True — убирает баннер «в стадии оформления»."
        ),
    )

    @property
    def legal_details_complete(self) -> bool:
        """Реквизиты готовы к публикации: ИНН и адрес заполнены и явно подтверждены."""
        return bool(
            self.LEGAL_DETAILS_CONFIRMED
            and self.LEGAL_OPERATOR_INN.strip()
            and self.LEGAL_OPERATOR_ADDRESS.strip()
        )

    @property
    def legal_context(self) -> dict[str, object]:
        """Реквизиты для шаблонов (документы + footer). Незаполненные поля —
        видимые человекочитаемые заглушки, чтобы в вёрстке не зияли пустоты."""
        return {
            "operator_name": self.LEGAL_OPERATOR_NAME,
            "operator_inn": self.LEGAL_OPERATOR_INN.strip() or "[ИНН — после регистрации юрлица]",
            "operator_address": self.LEGAL_OPERATOR_ADDRESS.strip()
            or "[адрес — после регистрации юрлица]",
            "contact_email": self.LEGAL_CONTACT_EMAIL,
            "doc_date": self.LEGAL_DOC_DATE.strip() or "[дата вступления в силу]",
            "retention_months": self.LEGAL_DATA_RETENTION_MONTHS,
            "complete": self.legal_details_complete,
        }


settings = Settings()


# Дефолтные значения секретов — их наличие в production недопустимо.
_DEFAULT_JWT_SECRET = "dev-insecure-secret-change-me-in-production-env-32b"


def validate_production_security(s: Settings) -> list[str]:
    """Возвращает список проблем безопасности конфигурации для production.

    В development всегда пусто — дефолты допустимы для локальной разработки.
    В production пустой список означает «можно стартовать»; непустой —
    приложение обязано упасть при старте (fail-loud), а не уехать в бой
    с дев-секретом или незащищённой cookie.
    """
    if not s.is_production:
        return []

    problems: list[str] = []
    if s.JWT_SECRET == _DEFAULT_JWT_SECRET or len(s.JWT_SECRET) < 32:
        problems.append("JWT_SECRET не задан или дефолтный — задайте стойкий секрет (>=32 симв.) в .env")
    if not s.COOKIE_SECURE:
        problems.append("COOKIE_SECURE=false — в production cookie должна иметь флаг Secure (нужен HTTPS)")
    if not s.ADMIN_API_KEY or len(s.ADMIN_API_KEY) < 16:
        problems.append("ADMIN_API_KEY не задан или слишком короткий — задайте стойкий ключ (>=16 симв.) в .env для защиты админ-эндпоинтов")
    return problems
