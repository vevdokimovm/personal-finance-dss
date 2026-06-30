"""Перешифровка данных «в покое» под новый ключ (SEC-4.4, ротация ключа).

Часть процедуры ротации Fernet-ключа: после того как новый ключ добавлен PRIMARY в
`TOKEN_ENCRYPTION_KEYS`, `reencrypt_all` проходит по всем полям `EncryptedString` и
переписывает их значения primary-ключом. После этого старый ключ можно убрать из
набора — данные больше от него не зависят.

Колонки определяются интроспекцией маппинга (не списком), поэтому новое
`EncryptedString`-поле автоматически попадает в перешифровку без правки этого файла.
Работает и со старо-зашифрованными значениями (читаются прежним ключом из набора),
и с legacy-незашифрованными (читаются как есть → шифруются primary).
"""
from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.database.db import Base
from app.database.types import EncryptedString


def encrypted_columns() -> list[tuple[type, str]]:
    """Все пары (модель, имя-атрибута) с колонкой EncryptedString."""
    found: list[tuple[type, str]] = []
    for mapper in Base.registry.mappers:
        for column in mapper.columns:
            if isinstance(column.type, EncryptedString):
                found.append((mapper.class_, column.key))
    return found


def reencrypt_all(db: Session) -> dict[str, int]:
    """Перешифровывает все EncryptedString-значения primary-ключом текущего набора.

    Возвращает число переписанных строк по таблицам. Переприсвоение + `flag_modified`
    форсят `process_bind_param` (шифрование primary), даже если строковое значение не
    изменилось — иначе SQLAlchemy счёл бы запись «чистой» и не переписал бы её.
    """
    counts: dict[str, int] = {}
    for model, attr in encrypted_columns():
        rewritten = 0
        for obj in db.query(model).all():
            value = getattr(obj, attr)
            if value is None:
                continue
            setattr(obj, attr, value)
            flag_modified(obj, attr)
            rewritten += 1
        if rewritten:
            counts[getattr(model, "__tablename__", model.__name__)] = rewritten
    db.commit()
    return counts
