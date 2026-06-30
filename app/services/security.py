"""Криптографические примитивы аутентификации и шифрования (INFRA-06, NFR-05, NFR-06, INFRA-17).

Три независимых ответственности:
  - PasswordHasher — bcrypt-хеш паролей (никогда не хранить открытый пароль).
  - TokenService   — выпуск/верификация JWT (stateless-сессия).
  - TokenCipher    — Fernet-шифрование Plaid access_token «в покое».

Класс-обёртки, без глобального состояния — конфиг приходит из app.config.settings.
"""
from __future__ import annotations

import base64
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Sequence

import bcrypt
import jwt
from cryptography.fernet import Fernet, InvalidToken, MultiFernet

from app.config import settings


class PasswordHasher:
    """bcrypt-хеширование паролей (NFR-05). Соль генерируется автоматически."""

    def hash(self, plain_password: str) -> str:
        salt = bcrypt.gensalt()
        digest = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return digest.decode("utf-8")

    def verify(self, plain_password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"), password_hash.encode("utf-8")
            )
        except (ValueError, TypeError):
            return False


class TokenService:
    """JWT access-токены (INFRA-06). HS256, срок жизни из конфига."""

    def __init__(
        self,
        secret: Optional[str] = None,
        algorithm: Optional[str] = None,
        ttl_hours: Optional[int] = None,
    ) -> None:
        self._secret = secret or settings.JWT_SECRET
        self._algorithm = algorithm or settings.JWT_ALGORITHM
        self._ttl_hours = ttl_hours if ttl_hours is not None else settings.JWT_TTL_HOURS

    def issue(self, user_id: str, email: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "email": email,
            "iat": now,
            "exp": now + timedelta(hours=self._ttl_hours),
            # Уникальный идентификатор токена — якорь для точечного отзыва (блок-лист).
            "jti": uuid.uuid4().hex,
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode(self, token: str) -> Optional[dict[str, Any]]:
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.PyJWTError:
            return None

    def issue_verification(self, user_id: str, email: str, ttl_hours: int = 48) -> str:
        """Токен подтверждения email (отдельное назначение, срок 48 ч)."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "email": email,
            "purpose": "email_verify",
            "iat": now,
            "exp": now + timedelta(hours=ttl_hours),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_verification(self, token: str) -> Optional[str]:
        """Возвращает user_id, если токен валиден и предназначен для верификации."""
        payload = self.decode(token)
        if not payload or payload.get("purpose") != "email_verify":
            return None
        return payload.get("sub")

    def issue_password_reset(self, user_id: str, email: str, ttl_hours: int = 1) -> str:
        """Токен сброса пароля (отдельное назначение, короткий срок)."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "email": email,
            "purpose": "password_reset",
            "iat": now,
            "exp": now + timedelta(hours=ttl_hours),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_password_reset(self, token: str) -> Optional[str]:
        """Возвращает user_id, если токен валиден и предназначен для сброса пароля."""
        payload = self.decode(token)
        if not payload or payload.get("purpose") != "password_reset":
            return None
        return payload.get("sub")

    def issue_telegram_link(self, user_id: str, email: str, ttl_hours: int = 1) -> str:
        """Одноразовый токен привязки Telegram (deep link `?start=<token>`)."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "email": email,
            "purpose": "telegram_link",
            "iat": now,
            "exp": now + timedelta(hours=ttl_hours),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_telegram_link(self, token: str) -> Optional[str]:
        """Возвращает user_id, если токен валиден и предназначен для привязки Telegram."""
        payload = self.decode(token)
        if not payload or payload.get("purpose") != "telegram_link":
            return None
        return payload.get("sub")


class TokenCipher:
    """Симметричное шифрование «в покое» (INFRA-17, NFR-06): Plaid-токены и поля
    EncryptedString.

    Ключи: набор из TOKEN_ENCRYPTION_KEYS (PRIMARY первым) для ротации; иначе один
    TOKEN_ENCRYPTION_KEY; иначе детерминированно производится из JWT_SECRET (dev
    работает без отдельного ключа, прод обязан задать собственный).

    Ротация (SEC-4.4): под капотом MultiFernet — primary шифрует, остальные ключи
    только читают. Чтобы сменить ключ без потери данных: новый ключ ставится первым
    в набор, прогоняется `reencrypt_all`, затем старый ключ убирается.
    """

    def __init__(self, keys: Optional[Sequence[str]] = None) -> None:
        resolved = self._resolve_keys(keys)
        self._mf = MultiFernet([Fernet(k.encode("utf-8")) for k in resolved])

    @staticmethod
    def _resolve_keys(keys: Optional[Sequence[str]]) -> list[str]:
        if keys:
            return list(keys)
        configured = settings.token_encryption_keys_list
        if configured:
            return configured
        derived = hashlib.sha256(settings.JWT_SECRET.encode("utf-8")).digest()
        return [base64.urlsafe_b64encode(derived).decode("utf-8")]

    def encrypt(self, plaintext: str) -> str:
        """Шифрует PRIMARY-ключом (первый в наборе)."""
        return self._mf.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> Optional[str]:
        """Расшифровывает, перебирая все ключи набора. None — если ни один не подошёл
        (чужой/повреждённый токен либо старое незашифрованное значение)."""
        try:
            return self._mf.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except (InvalidToken, ValueError):
            return None

    def rotate(self, ciphertext: str) -> Optional[str]:
        """Перешифровывает токен PRIMARY-ключом (для ротации). None — если значение
        не является валидным Fernet-токеном (legacy-plaintext шифруется через encrypt)."""
        try:
            return self._mf.rotate(ciphertext.encode("utf-8")).decode("utf-8")
        except (InvalidToken, ValueError):
            return None


password_hasher = PasswordHasher()
token_service = TokenService()
token_cipher = TokenCipher()
