"""E2E аутентификации в реальном браузере (переписано под React, v9.4.0).

## 🔴 Почему файл переписан целиком

Прежняя редакция была написана под **Jinja-вёрстку**: модалка `#auth-modal` в `base.html`,
управляемая `frontend/static/js/auth.js`, состояние в `#auth-status`. Всё это снесено
в вехе 8 — ни `app/templates`, ни `auth.js` больше не существует.

Тесты при этом **не были удалены и не были помечены**: они продолжали искать
несуществующие элементы и падать по таймауту. Проверено прогоном 06.09.2026:
**10 из 10 падали**, `TimeoutError: Locator.click: Timeout 30000ms exceeded`, — и на живом
CI то же самое. То есть красный сигнал шёл давно и принимался за фоновый шум.

**Что изменилось по существу, а не по селекторам.** Логин перестал быть модалкой:
это отдельные страницы `/login` и `/register` с типизированными search-параметрами
(`?redirect=`, `?ref=`). Состояние сессии видно в топбаре: email и «Выйти» у вошедшего,
«Войти» у гостя.

## Что эти сценарии проверяют, чего не видит ничто другое

Регистрация в браузере проходит через **настоящую цепочку**: форма → `POST /api/auth/register`
→ httpOnly-cookie от сервера → инвалидация `useProfile` → перерисовка топбара. Юнит-тест
проверяет каждое звено по отдельности и не видит разрывов между ними; именно такой разрыв
и был SEV1 `CONSENT-GATE-NO-UI` — бэкенд работал, интерфейса к нему не существовало.
"""
from __future__ import annotations

import time

import pytest

pytestmark = pytest.mark.e2e

PASSWORD = "strongpass123"  # ≥ 8 символов (требование register)


def _unique_email() -> str:
    return f"e2e-auth-{int(time.time() * 1000)}@test.io"


def _register(page, base_url: str, email: str) -> None:
    """Регистрация через страницу `/register` — как это делает человек.

    🔴 Согласие на обработку ПДн отмечается обязательно: без него форма не отправится
    (`required` на чекбоксе), и это не формальность интерфейса, а требование 152-ФЗ.
    """
    page.goto(f"{base_url}/register")
    page.wait_for_selector("#register-email", state="visible", timeout=15000)
    page.locator("#register-email").fill(email)
    page.locator("#register-password").fill(PASSWORD)
    page.locator('input[type="checkbox"][required]').check()
    page.get_by_role("button", name="Зарегистрироваться").click()


def _wait_logged_in(page, email: str) -> None:
    """Топбар показывает email — значит cookie принята и профиль перечитан.

    🔴 Ищем ИМЕННО в топбаре (`.fp-auth-topbar__email`), а не текстом по странице.
    Первая редакция искала `text={email}` — и мутационная проверка показала,
    что она зелёная даже когда топбар email не выводит вовсе: адрес остаётся
    в поле формы регистрации, и совпадение находится там.

    Тест, проходящий при сломанном предмете проверки, — это не тест.
    """
    page.wait_for_selector(f".fp-auth-topbar__email:has-text('{email}')", timeout=15000)


def _wait_guest(page) -> None:
    page.get_by_role("link", name="Войти").first.wait_for(state="visible", timeout=15000)


def test_guest_sees_login_and_no_logout(page, base_url) -> None:
    """Гость видит вход и не видит выхода.

    Проверка кажется тривиальной и не является ею: топбар держит последние успешные
    данные профиля даже когда рефетч упал на 401 (`stale-if-error` в TanStack Query),
    и без явной проверки `error` показывал бы «Выйти» вышедшему человеку.
    """
    page.goto(f"{base_url}/")
    _wait_guest(page)
    assert page.get_by_role("button", name="Выйти").count() == 0


def test_register_logs_in(page, base_url) -> None:
    """🔴 Регистрация СРАЗУ заводит сессию — без подтверждения почты.

    Решение продукта: письмо уходит фоном, вход не блокирует. Иначе на первом деплое
    без рабочего SMTP (а `docs/deploy_owner_checklist.md` прямо предупреждает, что почта
    может не успеть) ни один аккаунт не смог бы войти вовсе.
    """
    email = _unique_email()
    page.goto(f"{base_url}/")
    _wait_guest(page)

    _register(page, base_url, email)
    _wait_logged_in(page, email)


def test_logout_returns_to_guest(page, base_url) -> None:
    """Выход возвращает гостевое состояние.

    🔴 Проверяется именно **топбар после выхода**: cookie чистит сервер, а интерфейс
    обязан перечитать «кто я». Незамеченный выход опаснее незамеченного входа — человек
    уходит от чужого компьютера, считая, что вышел.
    """
    email = _unique_email()
    _register(page, base_url, email)
    _wait_logged_in(page, email)

    page.get_by_role("button", name="Выйти").click()
    _wait_guest(page)


def test_login_after_logout(page, base_url) -> None:
    """Полный круг: регистрация → выход → вход тем же паролем.

    Единственный сценарий, где проверяется, что пароль действительно сохранён и принят
    сервером, а не что форма «что-то отправила».
    """
    email = _unique_email()
    _register(page, base_url, email)
    _wait_logged_in(page, email)

    page.get_by_role("button", name="Выйти").click()
    _wait_guest(page)

    page.goto(f"{base_url}/login")
    page.wait_for_selector("#login-email", state="visible", timeout=15000)
    page.locator("#login-email").fill(email)
    page.locator("#login-password").fill(PASSWORD)
    page.get_by_role("button", name="Войти").last.click()

    _wait_logged_in(page, email)
