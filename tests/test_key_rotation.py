"""Ротация ключа шифрования «в покое» — Fernet MultiFernet (SEC-4.4).

Зачем. Один статический ключ нельзя сменить без потери данных: перешифровать старое
нечем, если старый ключ выброшен. MultiFernet решает: набор ключей, primary (первый)
шифрует, остальные — только читают. Процедура ротации:

  1. добавить новый ключ ПЕРВЫМ в `TOKEN_ENCRYPTION_KEYS` (новые записи → новый ключ,
     старые ещё читаются старым);
  2. прогнать `reencrypt_all` — все значения перезаписываются primary-ключом;
  3. убрать старый ключ из набора.

Контракт обратной совместимости: один ключ / derive из JWT_SECRET / legacy-незашифрованные
значения продолжают работать.
"""
from __future__ import annotations

import app.database.types as types_mod
from app.config import settings
from app.database.crud import create_user
from app.database.reencrypt import reencrypt_all
from app.services.security import TokenCipher, password_hasher
from cryptography.fernet import Fernet
from sqlalchemy import text


def _key() -> str:
    return Fernet.generate_key().decode()


# ── Уровень шифра: MultiFernet ────────────────────────────────────────────

def test_multifernet_reads_old_and_new_keys():
    old, new = _key(), _key()
    old_only = TokenCipher(keys=[old])
    token_old = old_only.encrypt("secret-note")
    # Набор [new, old] обязан прочитать токен, зашифрованный старым ключом.
    rotated_set = TokenCipher(keys=[new, old])
    assert rotated_set.decrypt(token_old) == "secret-note"


def test_encrypt_uses_primary_key():
    old, new = _key(), _key()
    cipher = TokenCipher(keys=[new, old])
    token = cipher.encrypt("secret-note")
    # Зашифровано primary (new): набор только с new читает, только со старым — нет.
    assert TokenCipher(keys=[new]).decrypt(token) == "secret-note"
    assert TokenCipher(keys=[old]).decrypt(token) is None


def test_rotate_reencrypts_to_primary():
    old, new = _key(), _key()
    token_old = TokenCipher(keys=[old]).encrypt("secret-note")
    rotated = TokenCipher(keys=[new, old]).rotate(token_old)
    assert rotated is not None
    # После rotate токен читается primary (new) в одиночку.
    assert TokenCipher(keys=[new]).decrypt(rotated) == "secret-note"


def test_decrypt_unknown_token_returns_none():
    cipher = TokenCipher(keys=[_key()])
    assert cipher.decrypt("not-a-fernet-token") is None


def test_rotate_legacy_plaintext_returns_none():
    cipher = TokenCipher(keys=[_key(), _key()])
    assert cipher.rotate("legacy-plaintext") is None


def test_single_key_roundtrip_backward_compatible():
    cipher = TokenCipher(keys=[_key()])
    assert cipher.decrypt(cipher.encrypt("x")) == "x"


# ── Уровень конфига: список ключей с приоритетами ─────────────────────────

def test_keys_list_prefers_multi(monkeypatch):
    monkeypatch.setattr(settings, "TOKEN_ENCRYPTION_KEYS", "k1, k2 , k3")
    monkeypatch.setattr(settings, "TOKEN_ENCRYPTION_KEY", "single")
    assert settings.token_encryption_keys_list == ["k1", "k2", "k3"]


def test_keys_list_falls_back_to_single(monkeypatch):
    monkeypatch.setattr(settings, "TOKEN_ENCRYPTION_KEYS", "")
    monkeypatch.setattr(settings, "TOKEN_ENCRYPTION_KEY", "single-key")
    assert settings.token_encryption_keys_list == ["single-key"]


# ── Уровень БД: перешифровка существующих данных ──────────────────────────

def _raw_display_name(db, email: str) -> str:
    return db.execute(
        text("SELECT display_name FROM users WHERE email = :e"), {"e": email}
    ).scalar()


def test_reencrypt_rewrites_with_primary(db_session, monkeypatch):
    old, new = _key(), _key()
    # Данные записаны старым ключом.
    monkeypatch.setattr(types_mod, "_cipher", TokenCipher(keys=[old]))
    user = create_user(db=db_session, email="rot@fp.io",
                       password_hash=password_hasher.hash("x"))
    user.display_name = "Тайное Имя"
    db_session.commit()
    raw_before = _raw_display_name(db_session, "rot@fp.io")
    assert TokenCipher(keys=[new]).decrypt(raw_before) is None  # new ещё не при делах

    # Ротация: new — primary, old оставлен для чтения; перешифровать всё.
    monkeypatch.setattr(types_mod, "_cipher", TokenCipher(keys=[new, old]))
    reencrypt_all(db_session)

    raw_after = _raw_display_name(db_session, "rot@fp.io")
    assert TokenCipher(keys=[new]).decrypt(raw_after) == "Тайное Имя"  # primary читает
    assert TokenCipher(keys=[old]).decrypt(raw_after) is None          # старый уже нет


def test_reencrypt_handles_legacy_plaintext(db_session, monkeypatch):
    new = _key()
    # Создаём запись и подкладываем в БД НЕзашифрованное legacy-значение напрямую.
    monkeypatch.setattr(types_mod, "_cipher", TokenCipher(keys=[new]))
    create_user(db=db_session, email="legacy@fp.io",
                password_hash=password_hasher.hash("x"))
    db_session.execute(
        text("UPDATE users SET display_name = :v WHERE email = :e"),
        {"v": "PlainLegacyName", "e": "legacy@fp.io"},
    )
    db_session.commit()
    db_session.expire_all()  # прямой SQL не виден в identity map — перечитать из БД

    reencrypt_all(db_session)

    raw = _raw_display_name(db_session, "legacy@fp.io")
    assert raw != "PlainLegacyName"  # больше не plaintext
    assert TokenCipher(keys=[new]).decrypt(raw) == "PlainLegacyName"


def test_reencrypt_returns_counts(db_session, monkeypatch):
    monkeypatch.setattr(types_mod, "_cipher", TokenCipher(keys=[_key()]))
    u = create_user(db=db_session, email="cnt@fp.io",
                    password_hash=password_hasher.hash("x"))
    u.display_name = "Имя"
    db_session.commit()
    counts = reencrypt_all(db_session)
    assert counts.get("users", 0) >= 1
