"""E2E аутентификации и гостевого режима (реальный браузер).

Закрывает то, чего не видят SSR/TestClient-тесты: что auth.js в браузере реально
отрисовывает гостевое/залогиненное состояние шапки, открывает модалку, шлёт
register/login и переключает UI. Логин у нас — не отдельная страница, а модалка
в base.html (`#auth-modal`), управляемая `frontend/static/js/auth.js`.

Наблюдаемые состояния (из auth.js):
  - гость:      #auth-status = "Гость", #auth-login-btn виден;
  - залогинен:  #auth-status = display_name|email, #auth-logout-btn виден.

Регистрация возвращает токен сразу (verify email — фоном, вход не блокирует),
поэтому happy-path register → залогинен проверяется в браузере без почты.
"""
from __future__ import annotations

import time

import pytest

pytestmark = pytest.mark.e2e

PASSWORD = "strongpass123"  # ≥ 8 символов (требование register)

STATUS_IS_GUEST = (
    "() => { const s = document.getElementById('auth-status');"
    " return s && s.textContent.trim() === 'Гость'; }"
)
STATUS_HAS = (
    "(needle) => { const s = document.getElementById('auth-status');"
    " return s && s.textContent.includes(needle); }"
)


def _unique_email() -> str:
    return f"e2e-auth-{int(time.time() * 1000)}@test.io"


def _open_auth_modal(page) -> None:
    # login-btn показывается JS только в гостевом состоянии — дожидаемся и кликаем
    page.wait_for_selector("#auth-login-btn", state="visible", timeout=15000)
    page.locator("#auth-login-btn").click()
    page.wait_for_selector("#auth-email", state="visible", timeout=5000)


def _register(page, email: str, *, name: str | None = None) -> None:
    _open_auth_modal(page)
    page.locator('[data-auth-tab="register"]').click()
    page.locator("#auth-email").fill(email)
    page.locator("#auth-password").fill(PASSWORD)
    if name:
        page.locator("#auth-name").fill(name)
    page.locator("#auth-consent").check()  # 152-ФЗ: согласие обязательно
    page.locator("#auth-submit").click()


def test_guest_mode_shows_login(page, base_url) -> None:
    page.goto("/")
    # JS отрисовал гостевое состояние шапки
    page.wait_for_function(STATUS_IS_GUEST, timeout=15000)
    assert page.locator("#auth-login-btn").is_visible()
    assert not page.locator("#auth-logout-btn").is_visible()


def test_register_logs_in(page, base_url) -> None:
    email = _unique_email()
    page.goto("/")
    page.wait_for_function(STATUS_IS_GUEST, timeout=15000)

    _register(page, email, name="E2E User")

    # Шапка переключилась в залогиненное состояние (имя или email)
    page.wait_for_function(STATUS_HAS, arg="E2E User", timeout=15000)
    page.wait_for_selector("#auth-logout-btn", state="visible", timeout=15000)


def test_logout_returns_to_guest(page, base_url) -> None:
    email = _unique_email()
    page.goto("/")
    page.wait_for_function(STATUS_IS_GUEST, timeout=15000)

    _register(page, email)
    page.wait_for_selector("#auth-logout-btn", state="visible", timeout=15000)

    page.locator("#auth-logout-btn").click()
    page.wait_for_function(STATUS_IS_GUEST, timeout=15000)
    assert page.locator("#auth-login-btn").is_visible()


def test_login_after_logout(page, base_url) -> None:
    email = _unique_email()
    page.goto("/")
    page.wait_for_function(STATUS_IS_GUEST, timeout=15000)

    # создаём аккаунт и сразу выходим
    _register(page, email)
    page.wait_for_selector("#auth-logout-btn", state="visible", timeout=15000)
    page.locator("#auth-logout-btn").click()
    page.wait_for_function(STATUS_IS_GUEST, timeout=15000)

    # входим тем же логином через UI (вкладка login активна по умолчанию)
    page.locator("#auth-login-btn").click()
    page.wait_for_selector("#auth-email", state="visible", timeout=5000)
    page.locator("#auth-email").fill(email)
    page.locator("#auth-password").fill(PASSWORD)
    page.locator("#auth-submit").click()

    page.wait_for_function(STATUS_HAS, arg=email, timeout=15000)
    page.wait_for_selector("#auth-logout-btn", state="visible", timeout=15000)
