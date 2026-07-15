#!/usr/bin/env python3
"""Перешифровка данных «в покое» под новый primary-ключ (SEC-4.4, ротация ключа).

Когда запускать. ПОСЛЕ того как новый Fernet-ключ добавлен ПЕРВЫМ в
`TOKEN_ENCRYPTION_KEYS` (старый оставлен в наборе для чтения):

    python scripts/reencrypt_keys.py

Печатает число перешифрованных строк по таблицам. Идемпотентен — повторный прогон
просто перепишет значения тем же primary. После успешного прогона старый ключ можно
безопасно убрать из `TOKEN_ENCRYPTION_KEYS`: данные от него больше не зависят.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.db import SessionLocal  # noqa: E402
from app.database.reencrypt import reencrypt_all  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        counts = reencrypt_all(db)
    finally:
        db.close()

    if not counts:
        print("Нечего перешифровывать (EncryptedString-поля пусты).")
        return

    total = sum(counts.values())
    print(f"Перешифровано строк: {total}")
    for table, number in sorted(counts.items()):
        print(f"  {table}: {number}")


if __name__ == "__main__":
    main()
