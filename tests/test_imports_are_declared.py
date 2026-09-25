"""Гейт: каждый сторонний импорт `app/` объявлен в requirements.

🔴 Оплачено красным CI на теге v9.13.16. В v9.13.14 разбор XML от ЦБ был переведён
на `defusedxml` (закрытие находки bandit B314) — и пакет не попал в `requirements.txt`.
Локально он стоял в венве, поэтому прогон был зелёным; на чистом раннере модуля нет,
и `conftest` не импортировался ВООБЩЕ: четыре джобы из девяти падали с
`ModuleNotFoundError: No module named 'defusedxml'` ещё до первого теста.

Класс — «работает у меня»: локальное окружение богаче объявленного, и расхождение
видно только на чистой машине. Ни один тест продукта его не ловит, потому что тесты
исполняются там же, где лишний пакет уже установлен.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
APP = REPO / "app"

# Имя пакета в PyPI не всегда совпадает с именем модуля.
DISTRIBUTION_BY_MODULE = {
    "dotenv": "python-dotenv",
    "jose": "python-jose",
    "multipart": "python-multipart",
    "dateutil": "python-dateutil",
    "yaml": "PyYAML",
    "PIL": "pillow",
    "jwt": "PyJWT",
    "psycopg2": "psycopg2-binary",
}


def _declared() -> set[str]:
    """Имена пакетов из обоих файлов требований, приведённые к нижнему регистру."""
    names: set[str] = set()
    for filename in ("requirements.txt", "requirements-dev.txt"):
        path = REPO / filename
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith(("#", "-")):
                continue
            name = re.split(r"[=<>!~\[;]", line)[0].strip()
            if name:
                names.add(name.lower().replace("_", "-"))
    return names


def _optional_imports(tree: ast.AST) -> set[str]:
    """Модули, импортируемые под `try/except ImportError`.

    Такой импорт — объявление необязательности: код сам обрабатывает отсутствие
    пакета (`plaid` поднимает понятный RuntimeError вместо падения). Требовать его
    в requirements значило бы тянуть в прод опциональную интеграцию.
    """
    optional: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        catches_import = any(
            handler.type is not None
            and "ImportError" in ast.unparse(handler.type)
            for handler in node.handlers
        )
        if not catches_import:
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Import):
                optional.update(alias.name.split(".")[0] for alias in inner.names)
            elif isinstance(inner, ast.ImportFrom) and inner.level == 0 and inner.module:
                optional.add(inner.module.split(".")[0])
    return optional


def _top_level_imports() -> dict[str, Path]:
    """Корневые модули, которые импортирует `app/`, и где это происходит."""
    found: dict[str, Path] = {}
    for source in APP.rglob("*.py"):
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        optional = _optional_imports(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split(".")[0]
                    if module not in optional:
                        found.setdefault(module, source)
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    module = node.module.split(".")[0]
                    if module not in optional:
                        found.setdefault(module, source)
    return found


class TestEveryThirdPartyImportIsDeclared:
    """Импорт, которого нет в requirements, валит прогон на чистой машине."""

    def test_no_undeclared_imports(self) -> None:
        declared = _declared()
        missing: list[str] = []
        for module, source in sorted(_top_level_imports().items()):
            if module in sys.stdlib_module_names or module in {"app", "tools", "tests"}:
                continue
            distribution = DISTRIBUTION_BY_MODULE.get(module, module)
            if distribution.lower().replace("_", "-") not in declared:
                missing.append(f"{module} ({source.relative_to(REPO)})")
        assert not missing, (
            "сторонние импорты не объявлены в requirements — на чистом раннере "
            "прогон упадёт до первого теста: " + "; ".join(missing)
        )

    def test_defusedxml_is_declared(self) -> None:
        """Именованная регрессия: ровно этот пакет уронил CI на теге v9.13.16."""
        assert "defusedxml" in _declared()
