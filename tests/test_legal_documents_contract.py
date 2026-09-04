"""Юридические тексты отдаются API из ЕДИНСТВЕННОГО источника (L7-остаток, v8.44.0).

## Зачем эндпоинт вообще

React-фронт не может показать политику обработки ПДн: её содержимое живёт только в
Jinja-шаблонах. Без эндпоинта фронту пришлось бы перепечатать юридический текст у себя —
и он разошёлся бы с официальным пакетом на первой же правке. Ровно этот класс закрывали
в v8.40.0 дисклеймером 39-ФЗ, который до того тоже не отдавался ответом.

## 🔴 Что вскрылось при разведке

Тексты УЖЕ существуют в двух редакциях:

- `docs/legal/*.md` — официальный пакет, «рабочие версии для вставки на сайт»
  (`docs/legal/README.md` §1), рядом лежат `docx/` для предъявления;
- `frontend/templates/legal/*.html` — рукописные копии в разметке, разошедшиеся с
  пакетом: у политики 97 строк против 87, разделы не совпадают.

Какая редакция показана пользователю — вопрос без ответа, а для 152-ФЗ ответ обязателен:
доказывать придётся тот текст, который человек видел. Поэтому источник ровно один —
`LEGAL_DOCUMENTS[*]["path"]`, то есть файлы `docs/legal/`, и API отдаёт их содержимое.

## Почему markdown, а не HTML

Официальный пакет ведётся в markdown, и `docx/` печатается из него же. Отдавать HTML
значило бы завести третью редакцию — конвертированную. Фронт рендерит markdown сам.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.core.legal import LEGAL_DOCUMENTS

REPO_ROOT = Path(__file__).resolve().parents[1]
OPENAPI = REPO_ROOT / "docs" / "api" / "openapi.json"

PUBLIC_SLUGS = ("privacy_policy", "terms_of_service", "cookie_policy")


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(OPENAPI.read_text(encoding="utf-8"))


class TestContract:
    def test_registry_endpoint_untouched(self, schema) -> None:
        """🔴 `/legal/documents` НЕ переделывается под новый экран.

        Он существует с v8.40.0 и питает ссылки футера (L7) на каждой странице,
        включая гостевые. Менять его форму ради удобства нового экрана значило бы
        сломать обязательный по закону элемент ради необязательного удобства —
        поэтому содержимое приезжает ОТДЕЛЬНЫМ эндпоинтом, а реестр остаётся как был.
        """
        op = schema["paths"]["/api/legal/documents"]["get"]
        ref = op["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        item = schema["components"]["schemas"][ref.rsplit("/", 1)[-1]]
        assert "documents" in item["properties"]
        assert "disclaimer_39fz" in item["properties"]

    def test_document_endpoint_is_typed(self, schema) -> None:
        op = schema["paths"]["/api/legal/documents/{slug}"]["get"]
        ref = op["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        name = ref.rsplit("/", 1)[-1]
        item = schema["components"]["schemas"][name]
        for field in ("slug", "title", "version", "effective_from", "content"):
            assert field in item["properties"], field
            assert field in item.get("required", []), (
                f"{field} необязателен — фронт получит undefined там, где обязан "
                f"показать юридически значимый текст"
            )


class TestServed:
    """Отдаётся то же, что в официальном пакете, а не пересказ."""

    @pytest.mark.parametrize("slug", PUBLIC_SLUGS)
    def test_content_matches_the_source_file(self, client, slug) -> None:
        response = client.get(f"/api/legal/documents/{slug}")
        assert response.status_code == 200, slug
        served = response.json()["content"]
        source = (REPO_ROOT / LEGAL_DOCUMENTS[slug]["path"]).read_text(encoding="utf-8")
        assert served.strip() == source.strip(), (
            f"{slug}: API отдаёт не то, что лежит в docs/legal — появилась вторая "
            f"редакция юридического текста"
        )

    @pytest.mark.parametrize("slug", PUBLIC_SLUGS)
    def test_metadata_comes_from_the_registry(self, client, slug) -> None:
        """Версия и дата — из реестра: по ним доказывают, на что человек согласился."""
        body = client.get(f"/api/legal/documents/{slug}").json()
        assert body["version"] == LEGAL_DOCUMENTS[slug]["version"]
        assert body["effective_from"] == LEGAL_DOCUMENTS[slug]["effective_from"]
        assert body["title"] == LEGAL_DOCUMENTS[slug]["title"]

    def test_registry_covers_every_public_document(self, client) -> None:
        slugs = set(client.get("/api/legal/documents").json()["documents"])
        for slug in PUBLIC_SLUGS:
            assert slug in slugs, f"{slug} не попал в реестр — ссылка футера ведёт в пустоту"

    def test_every_registry_entry_has_readable_content(self, client) -> None:
        """🔴 Реестр и содержимое обязаны сходиться ПОЛНОСТЬЮ.

        Документ, попавший в реестр (и, значит, в ссылку футера), но не отдающий текста,
        даёт пустую страницу на месте юридически обязательного документа. Это хуже
        отсутствия ссылки: ссылка есть, требование формально закрыто, а человек ничего
        не прочитал. Поэтому проверяется КАЖДЫЙ ключ реестра, а не список из теста —
        новый документ попадёт под проверку сам.
        """
        for slug in client.get("/api/legal/documents").json()["documents"]:
            response = client.get(f"/api/legal/documents/{slug}")
            assert response.status_code == 200, f"{slug} есть в реестре, но текста нет"
            assert response.json()["content"].strip(), f"{slug}: пустой текст"

    def test_unknown_slug_is_404_not_500(self, client) -> None:
        assert client.get("/api/legal/documents/no-such-doc").status_code == 404

    def test_slug_cannot_escape_the_registry(self, client) -> None:
        """🔴 Путь берётся из реестра по ключу, а не склеивается из ввода.

        Иначе `../../.env` читался бы с диска через публичный эндпоинт. Проверяется
        именно отказ, а не «содержимое пустое»: пустой ответ мог бы означать, что
        файла нет, а не что обход запрещён.

        Векторы — только те, что РЕАЛЬНО доходят до эндпоинта. Первая редакция проверяла
        `../../../etc/passwd` голым: такой путь нормализуется до отправки, до обработчика
        не доезжает вовсе, и тест утверждал невозможное (родня PIT-021 — проверка ожидала
        не того, что бывает). Закодированные формы проходят нормализацию и доходят.
        """
        for attack in ("..%2F..%2F.env", "%2e%2e%2f.env", "....//.env", "docs%2Flegal"):
            response = client.get(f"/api/legal/documents/{attack}")
            assert response.status_code in (404, 422), attack

    def test_spa_fallback_does_not_leak_files(self, client) -> None:
        """🔴 Catch-all SPA не отдаёт файлы за пределами сборки.

        Он обязан вернуть `index.html` на любой неизвестный адрес — и именно поэтому
        опасен: отдай он `../.env` как файл, ответ был бы 200 и выглядел бы нормально.
        Проверяется не код ответа (он всегда 200), а СОДЕРЖИМОЕ.
        """
        markers = ("DATABASE_URL", "JWT_SECRET", "fastapi==", "def create_app")
        for attack in ("../.env", "..%2F.env", "../../app/config.py", "%2e%2e/requirements.txt"):
            body = client.get(f"/{attack}").text
            assert not any(m in body for m in markers), f"{attack}: с диска утёк файл"


class TestPublic:
    """Документы читаются БЕЗ авторизации и без согласия.

    Политику обработки ПДн человек обязан прочитать ДО регистрации — иначе согласие
    неинформированное, и это дефект юридический, а не интерфейсный. Требовать согласия
    на обработку данных, чтобы прочитать условия обработки данных, — замкнутый круг.
    """

    @pytest.mark.parametrize("slug", PUBLIC_SLUGS)
    def test_available_to_anonymous(self, client, slug) -> None:
        assert client.get(f"/api/legal/documents/{slug}").status_code == 200

    def test_consent_texts_are_public_too(self, client) -> None:
        """Тексты самих согласий тоже: их показывают у чекбокса при регистрации."""
        assert client.get("/api/legal/documents/personal_data").status_code == 200
