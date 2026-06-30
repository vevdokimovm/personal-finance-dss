"""MFA/TOTP — генерация и проверка (раздел 4.4).

Тонкая обёртка над pyotp + генерация/хеширование одноразовых recovery-кодов.
Состояние (секрет, флаг, коды) живёт в БД (`crud`/`models`), здесь — только крипто.
"""
from __future__ import annotations

import secrets

import pyotp

from app.services.security import password_hasher

_ISSUER = "FINPILOT"
_RECOVERY_CODE_COUNT = 10


def generate_secret() -> str:
    """Новый base32-секрет TOTP."""
    return pyotp.random_base32()


def provisioning_uri(secret: str, account: str) -> str:
    """otpauth://-URI для QR в authenticator-приложении."""
    return pyotp.TOTP(secret).provisioning_uri(name=account, issuer_name=_ISSUER)


def verify_totp(secret: str, code: str) -> bool:
    """Проверяет TOTP-код. valid_window=1 — допускает соседнее 30-сек окно
    (компенсирует расхождение часов клиента и сервера)."""
    if not code or not code.strip():
        return False
    return pyotp.TOTP(secret).verify(code.strip(), valid_window=1)


def generate_recovery_codes(count: int = _RECOVERY_CODE_COUNT) -> list[str]:
    """Список читаемых одноразовых recovery-кодов (формат XXXX-XXXX, hex)."""
    codes = []
    for _ in range(count):
        raw = secrets.token_hex(4)  # 8 hex-символов
        codes.append(f"{raw[:4]}-{raw[4:]}")
    return codes


def hash_recovery_code(code: str) -> str:
    """Хеш recovery-кода для хранения (bcrypt, как пароль)."""
    return password_hasher.hash(code.strip())


def verify_recovery_code(code: str, code_hash: str) -> bool:
    """Сверяет recovery-код с хешем."""
    return password_hasher.verify(code.strip(), code_hash)
