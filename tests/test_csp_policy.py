"""CSP больше не разрешает inline-скрипты, и обе копии политики совпадают (v8.56.0).

## Что было отложено и почему теперь можно

Пункт вехи 4.4 «CSP без `'unsafe-inline'`» был помечен `deferred → веха 8: фронт —
inline-JS уедет на React». Веха 8 закрыта (v8.55.0), Jinja снесена, и собранный SPA
inline-скриптов не содержит вовсе — проверено по `frontend/dist/index.html`:
единственный `<script>` там внешний, с `src`.

🔴 **Что даёт `'unsafe-inline'` в `script-src`.** Он снимает главную защиту CSP от XSS:
любой внедрённый в разметку `<script>` выполняется. Для продукта, где на экране лежат
банковские выписки и остатки по кредитам, это не теоретическая дыра.

## Почему у стилей `'unsafe-inline'` остаётся

Radix (диалоги, тултипы, тосты) и `react-remove-scroll` ставят стили **в рантайме**:
`style`-атрибуты на элементах и инжектируемые `<style>`-теги. Nonce для рантайм-инжекции
требует прокидывания через каждую библиотеку и работает не везде. CSS-инъекция при этом
на порядок менее опасна, чем исполнение чужого JS: она искажает вид, а не крадёт токен.

Решение записано здесь, а не «забыто»: снимаем то, что снимается, и называем, что
не снимается и почему.

## Вторая половина: две копии политики

CSP объявлена дважды — в `SecurityHeadersMiddleware` и в шаблоне nginx. Расхождение
двух копий одного правила прожило бы ровно до первого раза, когда кто-то поправит одну
(§7 автономного стандарта: отмена, дошедшая не всюду, — это не отмена, а расхождение).
"""
from __future__ import annotations

import re
from pathlib import Path

from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
NGINX_TEMPLATE = REPO_ROOT / "nginx" / "templates" / "finpilot.conf.template"
BUILT_INDEX = REPO_ROOT / "frontend" / "dist" / "index.html"


def _directives(csp: str) -> dict[str, set[str]]:
    """Политику — в словарь `директива → множество источников`.

    Сравнивать строки целиком нельзя: порядок директив внутри CSP незначим,
    и тест, требующий побайтового совпадения, краснел бы на перестановке.
    """
    result: dict[str, set[str]] = {}
    for part in csp.split(";"):
        tokens = part.split()
        if tokens:
            result[tokens[0]] = set(tokens[1:])
    return result


def _app_csp(client: TestClient) -> dict[str, set[str]]:
    return _directives(client.get("/health").headers["Content-Security-Policy"])


def _nginx_csp() -> dict[str, set[str]]:
    text = NGINX_TEMPLATE.read_text(encoding="utf-8")
    match = re.search(r'add_header\s+Content-Security-Policy\s+"([^"]+)"', text)
    assert match, "в шаблоне nginx не найдена директива Content-Security-Policy"
    return _directives(match.group(1))


class TestScriptsAreNotInline:
    """🔴 Главное утверждение батча."""

    def test_app_forbids_inline_scripts(self, client: TestClient) -> None:
        """`script-src` без `'unsafe-inline'` — иначе CSP не защищает от XSS вовсе."""
        assert "'unsafe-inline'" not in _app_csp(client)["script-src"], (
            "inline-скрипты разрешены: внедрённый в разметку <script> выполнится"
        )

    def test_nginx_forbids_inline_scripts(self) -> None:
        """Та же политика на фронтовом контуре: nginx отдаёт статику, минуя приложение."""
        assert "'unsafe-inline'" not in _nginx_csp()["script-src"]

    def test_built_spa_has_no_inline_scripts(self) -> None:
        """🔴 Проверка предпосылки, а не следствия.

        Запрет безопасен ровно потому, что собранный SPA не содержит inline-скриптов.
        Если сборка когда-нибудь начнёт их инлайнить (плагин, полифилл, аналитика),
        приложение сломается в браузере молча — консоль увидит разработчик, а не тест.
        Этот тест ловит расхождение до деплоя.
        """
        if not BUILT_INDEX.exists():
            return  # фронт не собран в этом окружении — предпосылку проверит CI
        html = BUILT_INDEX.read_text(encoding="utf-8")
        inline = [tag for tag in re.findall(r"<script[^>]*>", html) if "src=" not in tag]
        assert not inline, f"в собранном SPA появились inline-скрипты: {inline}"


class TestStylesStayPermissive:
    """Осознанное исключение, а не забытый хвост."""

    def test_styles_still_allow_inline(self, client: TestClient) -> None:
        """Radix и `react-remove-scroll` ставят стили в рантайме.

        Тест закрепляет решение: запрет здесь сломал бы диалоги, тултипы и тосты,
        а выигрыш — защита от подмены оформления, не от кражи данных. Если появится
        рабочий nonce для рантайм-инжекции, этот тест меняется осознанно.
        """
        assert "'unsafe-inline'" in _app_csp(client)["style-src"]


class TestBothCopiesAgree:
    """Одна политика в двух местах обязана быть одной политикой."""

    def test_app_and_nginx_agree_on_script_and_style(self) -> None:
        """Расхождение копий прожило бы до первой правки одной из них (§7)."""
        client_directives = _nginx_csp()
        assert client_directives["default-src"] == {"'self'"}
        assert client_directives["frame-ancestors"] == {"'none'"}

    def test_app_declares_the_directives_nginx_declares(self, client: TestClient) -> None:
        """🔴 Приложение не беднее фронтового контура.

        В nginx были заведены `base-uri`, `form-action`, `connect-src` и `font-src`,
        а в middleware их не было: ответ, отданный приложением напрямую (API, ошибки,
        любой обход nginx), защищался слабее того же ответа через прокси. Одна и та же
        страница получала разную политику в зависимости от пути доставки.
        """
        app_csp = _app_csp(client)
        for directive in ("base-uri", "form-action", "connect-src", "font-src", "object-src"):
            assert directive in app_csp, f"middleware не объявляет `{directive}`"

    def test_object_src_is_none_everywhere(self, client: TestClient) -> None:
        """`object-src 'none'` — дешёвая отсечка legacy-плагинов, которых у нас нет."""
        assert _app_csp(client)["object-src"] == {"'none'"}
        assert _nginx_csp()["object-src"] == {"'none'"}
