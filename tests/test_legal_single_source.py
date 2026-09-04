"""У юридических параметров ОДИН источник, а не два противоречащих (v8.44.0).

## Что вскрылось

До этого батча продукт публиковал **две редакции одних и тех же документов**, и они
расходились по существу:

| | Jinja (`config.py` → `legal_context`) | пакет `docs/legal/*.md` |
|---|---|---|
| оператор | ООО «ФИНПАЙЛОТ» | сервис FINPILOT |
| срок хранения после удаления | 6 месяцев | 1 (один) год |
| адрес обращений | `support@finpilot.app` | `finpilot.help@proton.me` |

Расхождение нашёл design-critic при переносе документов в React. В споре два
противоречащих «настоящих текста» хуже, чем один неудобный: доказывать придётся тот,
который человек видел, а какой он видел — зависело от того, какой шаблон отрендерился.

## Кто прав

Пакет `docs/legal/`. Это записано в `docs/legal/README.md` §1 прямым текстом:
«Принятые параметры (менять только вместе во всех документах): оператор — сервис
FINPILOT без реквизитов юрлица (решение этапа MVP); адрес обращений и отзыва
согласий — `finpilot.help@proton.me`». Значения в `config.py` — заглушки более раннего
этапа, пережившие решение.

## Что проверяет этот гейт

Что параметры в коде не противоречат опубликованному тексту. Проза здесь уже не
работает: расхождение прожило от v6.25.0 до v8.44.0 при том, что оба файла лежали
рядом и оба читались.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from app.config import settings

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE = REPO_ROOT / "docs" / "legal"

PUBLISHED_TEXTS = [
    PACKAGE / "privacy-policy.md",
    PACKAGE / "terms-of-service.md",
    PACKAGE / "cookie-policy.md",
    PACKAGE / "consent-personal-data.md",
    PACKAGE / "consent-financial-data.md",
    PACKAGE / "consent-marketing.md",
]


@pytest.fixture(scope="module")
def published() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in PUBLISHED_TEXTS)


def test_contact_email_matches_the_published_package(published) -> None:
    """Адрес обращений — тот же, что напечатан в документах.

    По нему человек отзывает согласие и требует удаления данных: адрес, которого нет
    в тексте, делает право нереализуемым.
    """
    assert settings.LEGAL_CONTACT_EMAIL in published, (
        f"{settings.LEGAL_CONTACT_EMAIL} не встречается ни в одном документе пакета — "
        f"в коде и в опубликованном тексте разные адреса для обращений"
    )


def test_no_stale_contact_email_left_in_code() -> None:
    """Заглушка домена не должна пережить решение о реальном адресе."""
    assert not settings.LEGAL_CONTACT_EMAIL.endswith("@finpilot.app"), (
        "в коде остался адрес-заглушка, а пакет документов называет другой"
    )


def test_retention_matches_the_published_promise(published) -> None:
    """Срок хранения после удаления учётной записи — обещание пользователю.

    `LEGAL_DATA_RETENTION_MONTHS` подставляется в Jinja-редакцию, а пакет печатает
    свой срок словами. Разойтись они не имеют права: 6 месяцев против года — это
    полгода незаконного хранения либо неисполненное обещание, смотря какой текст
    предъявят.
    """
    months = settings.LEGAL_DATA_RETENTION_MONTHS
    variants = {
        12: ("1 (одного) года", "одного года", "12 месяцев"),
        6: ("6 (шести) месяцев", "шести месяцев", "6 месяцев"),
    }
    expected = variants.get(months)
    assert expected, f"срок {months} мес. не описан ни в одном документе пакета"
    assert any(text in published for text in expected), (
        f"в коде {months} мес., а в опубликованном тексте такого срока нет"
    )


def test_operator_name_matches_the_published_package(published) -> None:
    """Наименование оператора — то же, что в документах.

    Пакет принял решение этапа MVP: оператор — «сервис FINPILOT», без реквизитов
    юрлица. Название юрлица в коде, которого нет в тексте, означает, что документ
    подписан не тем, кто в нём назван.
    """
    name = settings.LEGAL_OPERATOR_NAME
    core = name.strip("«»\" ").replace("ООО ", "")
    assert core.lower() in published.lower() or name in published, (
        f"оператор в коде — {name!r}, а в документах пакета такого наименования нет"
    )


def test_every_registry_path_exists() -> None:
    """Реестр ссылается на существующие файлы.

    Путь из реестра теперь читается на рантайме (`GET /legal/documents/{slug}`):
    опечатка в нём даёт 503 на юридически обязательном документе, а не тихий промах.
    """
    from app.core.legal import LEGAL_DOCUMENTS

    for slug, doc in LEGAL_DOCUMENTS.items():
        assert (REPO_ROOT / doc["path"]).is_file(), f"{slug}: нет файла {doc['path']}"
