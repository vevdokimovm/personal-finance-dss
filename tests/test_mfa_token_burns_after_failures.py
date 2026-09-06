"""`mfa_pending`-токен сгорает после N неудачных кодов (v9.2.0).

## Вторая половина защиты, начатой в v9.1.0

В v9.1.0 префикс `/api/auth/mfa/` попал под rate-limit: без него атакующий, знающий
пароль, получал пятиминутный `mfa_pending`-токен и бросал в шестизначный TOTP
неограниченное число догадок. Второй фактор переставал быть фактором.

🔴 **Лимит ограничивает частоту, а не общее число попыток.** За пять минут жизни токена
разрешённых лимитом обращений набирается достаточно, чтобы заметно сдвинуть шансы:
пространство TOTP — миллион кодов, окно приёма покрывает несколько из них, и каждая
сотня попыток это не «ничтожная доля», а сотня.

**Правильная граница — сам токен.** Он выдан под ОДИН вход; несколько неверных кодов
подряд означают либо ошибку человека (он повторит вход, это дёшево), либо перебор.
Сгоревший токен заставляет пройти пароль заново — и вот там уже стоит и лимит,
и учёт неудачных входов.

## Почему счётчик привязан к токену, а не к пользователю

Счётчик на пользователе выглядит строже и на деле слабее: атакующий, знающий пароль,
повторным входом получает новый токен и **сбрасывает** счётчик. Привязка к токену
делает каждую попытку перебора дороже ровно на один полный вход — то есть переносит
стоимость туда, где уже есть защита.

Обратная сторона — счётчик обязан переживать перезапуск и жить одинаково у всех
рабочих процессов, поэтому он в базе, а не в памяти: продукт за gunicorn с четырьмя
воркерами хранил бы в памяти четыре независимых счётчика, и порог умножился бы на
число воркеров, никак этого не показав.
"""
from __future__ import annotations

import pyotp
from fastapi import status
from fastapi.testclient import TestClient

MAX_ATTEMPTS = 5


def _enrol_mfa(client: TestClient, email: str) -> tuple[str, str]:
    """Заводит пользователя со включённым вторым фактором. Возвращает (пароль, секрет)."""
    password = "password123"
    registered = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "consent": True},
    )
    assert registered.status_code in (200, 201), registered.text
    headers = {"Authorization": f"Bearer {registered.json()['access_token']}"}

    enrolled = client.post("/api/auth/mfa/enroll", headers=headers, json={})
    assert enrolled.status_code in (200, 201), enrolled.text
    secret = enrolled.json()["secret"]

    confirmed = client.post(
        "/api/auth/mfa/confirm",
        headers=headers,
        json={"code": pyotp.TOTP(secret).now()},
    )
    assert confirmed.status_code in (200, 201), confirmed.text
    return password, secret


def _login_for_mfa_token(client: TestClient, email: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code in (200, 401, 202), response.text
    body = response.json()
    token = body.get("mfa_token")
    assert token, f"вход не вернул mfa_token: {body}"
    return token


class TestTokenBurnsAfterRepeatedFailures:
    """Перебор по одному токену упирается в потолок, а не в таймер."""

    def test_token_is_refused_after_the_limit_even_with_the_right_code(
        self, client: TestClient
    ) -> None:
        """🔴 Главная проверка: сгоревший токен не оживает от ВЕРНОГО кода.

        Без неё легко написать защиту, которая считает неудачи и всё равно
        пропускает угаданный код — то есть ровно ту, которой перебор и добивается.
        """
        email = "mfa-burn@test.io"
        password, secret = _enrol_mfa(client, email)
        token = _login_for_mfa_token(client, email, password)

        for _ in range(MAX_ATTEMPTS):
            client.post("/api/auth/mfa/verify", json={"mfa_token": token, "code": "000000"})

        response = client.post(
            "/api/auth/mfa/verify",
            json={"mfa_token": token, "code": pyotp.TOTP(secret).now()},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, (
            "верный код принят по сгоревшему токену — счётчик считает, но не защищает"
        )

    def test_a_fresh_login_still_works(self, client: TestClient) -> None:
        """Сгорел токен, а не аккаунт.

        🔴 Проверка против переусердствования: запирать аккаунт после пяти опечаток
        значит воспроизвести дефект гипотезы 9 (v9.0.0), где включённый второй фактор
        запирал вход НАВСЕГДА. Человек ошибся — он входит заново, и это должно работать.
        """
        email = "mfa-relogin@test.io"
        password, secret = _enrol_mfa(client, email)
        burned = _login_for_mfa_token(client, email, password)
        for _ in range(MAX_ATTEMPTS):
            client.post("/api/auth/mfa/verify", json={"mfa_token": burned, "code": "000000"})

        fresh = _login_for_mfa_token(client, email, password)
        assert fresh != burned, "повторный вход выдал ТОТ ЖЕ токен — сжигать его бесполезно"

        response = client.post(
            "/api/auth/mfa/verify",
            json={"mfa_token": fresh, "code": pyotp.TOTP(secret).now()},
        )
        assert response.status_code == status.HTTP_200_OK, response.text

    def test_a_few_mistakes_do_not_burn_the_token(self, client: TestClient) -> None:
        """До порога токен живой: человек ошибается, и это норма.

        Порог, срабатывающий с первой опечатки, был бы неотличим от поломки —
        и его сняли бы целиком.
        """
        email = "mfa-typos@test.io"
        password, secret = _enrol_mfa(client, email)
        token = _login_for_mfa_token(client, email, password)

        for _ in range(MAX_ATTEMPTS - 1):
            failed = client.post(
                "/api/auth/mfa/verify", json={"mfa_token": token, "code": "000000"}
            )
            assert failed.status_code == status.HTTP_401_UNAUTHORIZED

        response = client.post(
            "/api/auth/mfa/verify",
            json={"mfa_token": token, "code": pyotp.TOTP(secret).now()},
        )
        assert response.status_code == status.HTTP_200_OK, (
            "верный код отвергнут ДО порога — считаются не те попытки"
        )

    def test_each_token_counts_separately(self, client: TestClient) -> None:
        """🔴 Счётчик привязан к токену, а не к пользователю.

        Мутация «считать неудачи на пользователе» роняет этот тест: второй токен
        начинал бы с исчерпанным счётчиком, и человек, ошибившийся пять раз и вошедший
        заново, не смог бы войти вообще — при том что пароль он знает.
        """
        email = "mfa-per-token@test.io"
        password, secret = _enrol_mfa(client, email)

        first = _login_for_mfa_token(client, email, password)
        for _ in range(MAX_ATTEMPTS):
            client.post("/api/auth/mfa/verify", json={"mfa_token": first, "code": "000000"})

        second = _login_for_mfa_token(client, email, password)
        response = client.post(
            "/api/auth/mfa/verify",
            json={"mfa_token": second, "code": pyotp.TOTP(secret).now()},
        )
        assert response.status_code == status.HTTP_200_OK, (
            "новый токен унаследовал счётчик старого — считается пользователь, не токен"
        )


class TestRecoveryCodesShareTheLimit:
    """Recovery-код — второй путь через ту же дверь, и потолок у них общий."""

    def test_burned_token_refuses_recovery_codes_too(self, client: TestClient) -> None:
        """🔴 Отдельный потолок на каждый способ удваивает число попыток.

        `mfa_verify` принимает TOTP **или** recovery-код одним обращением. Считать
        их порознь значило бы дать атакующему два независимых бюджета догадок,
        а recovery-коды к тому же не меняются со временем.
        """
        email = "mfa-recovery@test.io"
        password, secret = _enrol_mfa(client, email)
        token = _login_for_mfa_token(client, email, password)

        # 🔴 Формат recovery-кода — `XXXX-XXXX` (hex), схема держит `max_length=16`.
        # Первая редакция теста слала строку длиннее, получала 422 на валидации
        # и до обработчика не доходила вовсе: пять «попыток», ни одной попытки.
        # Тест, чьи данные отвергает схема, проверяет схему, а не предмет.
        for _ in range(MAX_ATTEMPTS):
            failed = client.post(
                "/api/auth/mfa/verify",
                json={"mfa_token": token, "code": "dead-beef"},
            )
            assert failed.status_code == status.HTTP_401_UNAUTHORIZED, failed.text

        # 🔴 Проверять ВЕРНЫМ TOTP, а не ещё одним неверным кодом. Нашла мутационная
        # проверка: с порогом 9999 этот тест оставался зелёным, потому что неверный
        # код возвращает 401 и без всякого сжигания. Тест не различал «токен сгорел»
        # и «код просто неправильный» — то есть не проверял ничего.
        response = client.post(
            "/api/auth/mfa/verify",
            json={"mfa_token": token, "code": pyotp.TOTP(secret).now()},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, (
            "верный TOTP принят после исчерпания попыток recovery-кодами — "
            "значит у двух способов РАЗНЫЕ бюджеты догадок"
        )
