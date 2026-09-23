from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]
# 🔴 В корне РЕПОЗИТОРИЯ, а не выше него (исправлено v9.1.0, нашёл `/code-review`).
# Здесь стоял `BASE_DIR.parent`, то есть каталог над репой: README велит скопировать
# `.env.example` в `.env`, `.gitignore` этот файл прячет — а приложение его не читало
# и молча стартовало на дефолтах. При нативном запуске это означало боевой сервер
# в dev-конфигурации: `validate_production_security` молчит, `require_admin` пропускает
# всех при пустом ключе, проверка CSRF для cookie без Origin выключена.
ENV_FILE = BASE_DIR / ".env"


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
        default="9.12.62",
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
    TELEMETRY_COLLECTION_ENABLED: bool = Field(
        default=False,
        description=(
            "Телеметрия принятия совета (волна 0, п. 0.6, docs/model/telemetry_spec.md). "
            "False по умолчанию — намеренно: правовой контур обезличивания для "
            "использования этих данных в сертификации модели (152-ФЗ, ROADMAP §8.2а) "
            "закрывается юристом отдельно от кода. Переключать в True — решение "
            "владельца ПОСЛЕ закрытия контура, не автоматика при деплое."
        ),
    )
    CORS_ORIGINS: str = Field(
        default=(
            "http://localhost:8000,http://127.0.0.1:8000,"
            "http://localhost:5173,http://127.0.0.1:5173"
        ),
        description=(
            "Разрешённые источники CORS через запятую (INFRA-12). "
            "5173 — Vite dev-server (frontend/), веха 8, Э2+; прод переопределяет env-переменной."
        ),
    )
    TRUST_PROXY_HEADERS: bool = Field(
        default=False,
        description=(
            "Доверять ли `X-Forwarded-For` при определении клиента (v8.57.0). "
            "🔴 ВЫКЛЮЧЕН по умолчанию: заголовок ставит клиент, и с доверием «всегда» "
            "атакующий шлёт новый адрес на каждый запрос — счётчик не наберётся никогда, "
            "то есть rate-limit обходится одной строкой. Включать ТОЛЬКО там, где перед "
            "приложением стоит наш nginx: он выставляет заголовок сам и затирает "
            "клиентский. Без него за прокси лимит считает всех пользователей как одного "
            "и отвечает 429 всем сразу."
        ),
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
        description="Fernet-ключ шифрования Plaid-токенов (INFRA-17). "
                    "Пусто = derive из JWT_SECRET.",
    )
    TOKEN_ENCRYPTION_KEYS: str = Field(
        default="",
        description="Набор Fernet-ключей через запятую для ротации, PRIMARY первым "
                    "(SEC-4.4). Primary шифрует, остальные читают. Пусто → "
                    "TOKEN_ENCRYPTION_KEY → derive из JWT_SECRET.",
    )

    @property
    def token_encryption_keys_list(self) -> list[str]:
        """Ключи шифрования «в покое», PRIMARY первым. Приоритет источников:
        TOKEN_ENCRYPTION_KEYS (набор) → TOKEN_ENCRYPTION_KEY (один). Пусто →
        TokenCipher делает derive из JWT_SECRET."""
        multi = [k.strip() for k in self.TOKEN_ENCRYPTION_KEYS.split(",") if k.strip()]
        if multi:
            return multi
        single = self.TOKEN_ENCRYPTION_KEY.strip()
        return [single] if single else []

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

    # ── Telegram-бот (P3.6) ────────────────────────────────────────────
    # Пусто = бот выключен (no-op, как почта). Токен — от @BotFather.
    TELEGRAM_BOT_TOKEN: str = Field(
        default="", description="Токен бота от @BotFather. Пусто = выключен.")
    TELEGRAM_BOT_USERNAME: str = Field(
        default="", description="Username бота без @ (для deep link).")
    TELEGRAM_WEBHOOK_SECRET: str = Field(
        default="",
        description="Secret для валидации webhook (заголовок X-Telegram-Bot-Api-Secret-Token).",
    )

    @property
    def telegram_enabled(self) -> bool:
        return bool(self.TELEGRAM_BOT_TOKEN)

    # ── Юридические реквизиты оператора (P1.1, 152-ФЗ) ─────────────────
    # Подставляются в опубликованные документы и footer из единого места.
    # ИНН и адрес по умолчанию пусты: их нельзя выдумывать — это реальные
    # регистрационные данные. Пока не заполнены и флаг ниже не выставлен,
    # на юр-страницах показывается баннер «документ в стадии оформления».
    LEGAL_OPERATOR_NAME: str = Field(
        default="сервис FINPILOT",
        description=(
            "Наименование оператора ПДн. Совпадает с опубликованным пакетом "
            "(docs/legal/README.md §1: решение этапа MVP — оператор без реквизитов "
            "юрлица). Гейт: tests/test_legal_single_source.py."
        ),
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
        default="finpilot.help@proton.me",
        description=(
            "Адрес обращений и отзыва согласий. Напечатан в самих документах — по нему "
            "человек реализует права по 152-ФЗ, поэтому расходиться с текстом нельзя."
        ),
    )
    LEGAL_DOC_DATE: str = Field(
        default="",
        description="Дата вступления документов в силу (YYYY-MM-DD). Пусто = не указана.",
    )
    LEGAL_DATA_RETENTION_MONTHS: int = Field(
        default=12,
        ge=0,
        description=(
            "Срок хранения данных после удаления учётной записи, месяцев. 🔴 Это "
            "обещание пользователю, напечатанное в политике словами («1 (одного) "
            "года», privacy-policy.md §6.3). Было 6 при годе в тексте — полгода "
            "расхождения между кодом и обязательством."
        ),
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
        problems.append(
            "JWT_SECRET не задан или дефолтный — задайте стойкий секрет (>=32 симв.) в .env")
    if not s.COOKIE_SECURE:
        problems.append(
            "COOKIE_SECURE=false — в production cookie должна иметь флаг Secure (нужен HTTPS)")
    if not s.ADMIN_API_KEY or len(s.ADMIN_API_KEY) < 16:
        problems.append(
            "ADMIN_API_KEY не задан или слишком короткий — задайте стойкий ключ "
            "(>=16 симв.) в .env для защиты админ-эндпоинтов")
    if not (s.TOKEN_ENCRYPTION_KEYS.strip() or s.TOKEN_ENCRYPTION_KEY.strip()):
        problems.append(
            "TOKEN_ENCRYPTION_KEY(S) не задан — в production ключ шифрования «в покое» "
            "должен быть явным; иначе он деривится из JWT_SECRET (нет разделения ключей "
            "по назначению, ротация ключа шифрования невозможна). Задайте Fernet-ключ в .env")

    # 🔴 Ниже — проверки, которые ловят не взлом, а ТИХУЮ поломку прода (v8.56.0).
    # Общее у них: дефолт удобен в разработке, губителен в бою и не даёт ошибки
    # при старте, так что узнаёт о нём первый живой пользователь, а не мы.
    origins = s.cors_origins_list
    bad_origins = [
        o for o in origins
        if "localhost" in o or "127.0.0.1" in o or o.startswith("http://")
    ]
    if not origins or bad_origins:
        problems.append(
            "CORS_ORIGINS содержит локальные или незащищённые источники "
            f"({', '.join(bad_origins) or 'список пуст'}) — CSRFMiddleware отвергнет "
            "каждый POST/PUT/PATCH/DELETE с боевого домена, и сайт будет открываться, "
            "ничего не сохраняя. Задайте https-домены продукта в .env")
    if not s.TRUST_PROXY_HEADERS:
        problems.append(
            "TRUST_PROXY_HEADERS=false — за nginx rate-limit считает клиентом сам прокси, "
            "то есть всех пользователей как одного: лимит тратится вместе, и, исчерпав "
            "его, продукт отвечает 429 ВСЕМ сразу. Включите на проде (нашёл /code-review)")
    # 🔴 Почта обязательна на проде: без неё сброс пароля и подтверждение адреса —
    # тихий no-op, а `/auth/forgot-password` при этом отвечает «ссылка отправлена».
    # Человек, забывший пароль, теряет аккаунт навсегда и не понимает почему: это
    # ЕДИНСТВЕННЫЙ путь восстановления доступа. Прежде такая сборка проходила старт
    # молча — «первый деплой без SMTP» считался рабочей конфигурацией.
    # Цена ошибки несимметрична: не поднявшийся прод чинится строкой в `.env` и виден
    # сразу, потерянный доступ не чинится вовсе и виден не владельцу, а пользователю.
    if not s.email_enabled:
        problems.append(
            "почта не настроена (SMTP_HOST/SMTP_USER/SMTP_PASSWORD) — без неё "
            "не работают сброс пароля и подтверждение адреса, а пользователю "
            "при этом отвечают «ссылка отправлена»; восстановить доступ будет нечем")
    if s.DATABASE_URL.strip().lower().startswith("sqlite"):
        problems.append(
            "DATABASE_URL указывает на SQLite — в контейнере это файл, который исчезает "
            "при первом же пересоздании, вместе с финансовыми данными пользователей "
            "и без единой ошибки. Задайте PostgreSQL в .env")
    return problems
