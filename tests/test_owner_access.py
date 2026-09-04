"""Админские данные доступны владельцу продукта по ВХОДУ, а не только по ключу (v8.48.0).

## Решение владельца

Развилка стояла в ROADMAP: аналитика (`/analytics/*`) и управление A/B-экспериментами
(`/admin/experiments`) защищены `ADMIN_API_KEY` из `.env` — то есть посмотреть их можно
только через `curl`. Три варианта: раздел за ключом в браузере · признак владельца
в аккаунте · оставить API-only. Владелец выбрал **признак владельца** (04.09.2026).

🔴 **Почему не ключ в браузере.** Его пришлось бы хранить в `localStorage`, откуда
достаёт любой скрипт на странице, и это секрет за пределами `.env` — против правила
проекта. Признак в базе переиспользуется (поддержка, будущие роли) и не заводит секрета.

## 🔴 Что вскрылось при написании гейта

`require_admin` в **development при пустом ключе пропускает всех** — сознательно, чтобы
не мешать локальной разработке (`app/dependencies.py`). Значит проверка «обычный
пользователь получает отказ» в dev-конфигурации была бы ложно зелёной или ложно красной
в зависимости от того, задан ли ключ в окружении прогона.

Поэтому тесты разграничения **явно задают ключ** через monkeypatch: они проверяют
поведение продакшен-конфигурации, а не то, как настроена машина разработчика.
Родня PIT-021 — проверка обязана отвечать на заданный вопрос, а не на удобный.
"""
from __future__ import annotations

import pytest

from app.config import settings
from app.database.models import User

# Реальные пути (проверено по `app/api/`): аналитика и управление экспериментами.
ADMIN_PATHS = [
    ("get", "/api/analytics/overview"),
    ("get", "/api/analytics/funnel"),
    ("get", "/api/admin/experiments"),
]

TEST_KEY = "test-admin-key-for-gate"


@pytest.fixture(autouse=True)
def admin_key_is_set(monkeypatch):
    """Ключ задан всегда: иначе `require_admin` в dev пропускает всех, и половина
    проверок этого файла теряет смысл, оставаясь зелёной."""
    monkeypatch.setattr(settings, "ADMIN_API_KEY", TEST_KEY)


def _register(client, email: str) -> str:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "consent": True},
    )
    return response.json()["access_token"]


@pytest.mark.parametrize("method,path", ADMIN_PATHS)
def test_ordinary_user_is_refused(client, method, path) -> None:
    """🔴 Обычный вошедший пользователь админских данных не видит.

    Это данные о ВСЕХ пользователях: сколько регистраций, где отваливаются, какая группа
    эксперимента что показала. Открыть их каждому вошедшему значило бы раздать статистику
    по чужому поведению.
    """
    token = _register(client, f"plain-{path.replace('/', '-')}@test.io")
    response = getattr(client, method)(path, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403, (
        f"{method.upper()} {path} доступен обычному пользователю — {response.status_code}"
    )


@pytest.mark.parametrize("method,path", ADMIN_PATHS)
def test_guest_is_refused(client, method, path) -> None:
    """Гостю — тем более. Проверяется отдельно: у гостя нет токена, путь другой."""
    response = getattr(client, method)(path)
    assert response.status_code in (401, 403), f"{method.upper()} {path} открыт гостю"


@pytest.mark.parametrize("method,path", ADMIN_PATHS)
def test_owner_gets_access_without_key(client, db_session, method, path) -> None:
    """Владелец продукта видит данные без ключа и без терминала.

    Ради этого признак и заводится: до v8.48.0 смотреть аналитику можно было только
    `curl` с ключом из `.env`.
    """
    email = f"owner-{path.replace('/', '-')}@test.io"
    token = _register(client, email)
    user = db_session.query(User).filter(User.email == email).first()
    user.is_owner = True
    db_session.commit()

    response = getattr(client, method)(path, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, (
        f"{method.upper()} {path} закрыт для владельца — {response.status_code}"
    )


@pytest.mark.parametrize("method,path", ADMIN_PATHS)
def test_admin_key_still_works(client, method, path) -> None:
    """🔴 Ключ продолжает работать: им ходят скрипты и cron, у них нет аккаунта.

    Заменить ключ признаком владельца значило бы сломать автоматизацию, которая
    к интерфейсу отношения не имеет.
    """
    response = getattr(client, method)(path, headers={"X-Admin-Key": TEST_KEY})
    assert response.status_code == 200, (
        f"{method.upper()} {path} перестал принимать ADMIN_API_KEY — сломана автоматизация"
    )


def test_owner_flag_defaults_to_false(client, db_session) -> None:
    """Новый пользователь владельцем НЕ становится.

    Признак раздаётся вручную и осознанно. Значение по умолчанию `True` открыло бы
    статистику каждому зарегистрировавшемуся — и обнаружилось бы это не сразу.
    """
    _register(client, "fresh-user@test.io")
    user = db_session.query(User).filter(User.email == "fresh-user@test.io").first()
    assert user is not None
    assert user.is_owner is False


def test_me_tells_the_frontend_who_is_owner(client, db_session) -> None:
    """🔴 `/auth/me` отдаёт `is_owner` — иначе фронт не знает, показывать ли раздел.

    Без этого поля у интерфейса два одинаково плохих выхода: показать пункт меню всем
    и упереться в 403 (кнопка, ведущая в отказ — [IA-04]), либо не показывать никому,
    и тогда признак в базе бесполезен.

    Признак не секрет: он говорит только о том, что у ЭТОГО аккаунта есть доступ,
    и виден лишь его владельцу в ответе о самом себе.
    """
    email = "owner-me@test.io"
    token = _register(client, email)
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/auth/me", headers=headers).json()["is_owner"] is False

    user = db_session.query(User).filter(User.email == email).first()
    user.is_owner = True
    db_session.commit()

    assert client.get("/api/auth/me", headers=headers).json()["is_owner"] is True
