"""Шифруемые типы колонок (P1.6).

EncryptedString прозрачно шифрует строковое поле «в покое» (Fernet, тот же
TokenCipher, что и для Plaid-токенов). На чтение незашифрованные значения
возвращаются как есть — обратная совместимость без обязательной миграции данных.

Применять только к полям, по которым нет поиска/фильтрации и которые не участвуют
в расчётах (заметки, имя). email и денежные суммы шифровать так нельзя.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator

from app.services.security import TokenCipher

_cipher: Optional[TokenCipher] = None


def _get_cipher() -> TokenCipher:
    global _cipher
    if _cipher is None:
        _cipher = TokenCipher()
    return _cipher


class EncryptedString(TypeDecorator):
    """Строка, шифруемая Fernet при записи и расшифровываемая при чтении."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        if value is None:
            return None
        return _get_cipher().encrypt(str(value))

    def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
        if value is None:
            return None
        decrypted = _get_cipher().decrypt(value)
        # Не расшифровалось → старое незашифрованное значение, возвращаем как есть.
        return decrypted if decrypted is not None else value
