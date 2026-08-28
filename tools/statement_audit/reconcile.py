"""
Сверка импорта выписки с контрольными итогами банка — CLI поверх продуктового модуля.

Зачем: тесты на фикстурах доказывают, что парсер не сломался, но не доказывают, что он
верно прочитал КОНКРЕТНЫЙ файл. Почти каждая выписка объявляет собственные контрольные
суммы (поступления, расходы, обороты) — сверка с ними доказывает корректность импорта на
живом файле без ручной выверки. Именно так были пойманы дефекты, невидимые глазом:
кешбэк, уходивший в расход, и «Установка кредитного лимита» +110 000 ₽ как доход.

Логика ровно та же, что в проде (`app/services/statement_reconcile.py`) — инструмент лишь
печатает результат. Работает по пути к файлу на диске: реальные выписки содержат ПДн и в
репозиторий не кладутся.

Запуск:
    python -m tools.statement_audit.reconcile ~/Downloads/vypiska.pdf [ещё.pdf ...]
"""
from __future__ import annotations

import sys
from pathlib import Path

from app.services.statement_parser import (
    detect_pdf_bank,
    parse_bank_pdf,
    pdf_non_statement_reason,
)
from app.services.statement_reconcile import reconcile_statement

RESET, RED, GREEN, YELLOW, BOLD = "\033[0m", "\033[91m", "\033[92m", "\033[93m", "\033[1m"


def info(msg: str) -> None:
    print(f"{YELLOW}→{RESET} {msg}")


def ok(msg: str) -> None:
    print(f"{GREEN}✓{RESET} {msg}")


def warn(msg: str) -> None:
    print(f"{YELLOW}⚠{RESET} {msg}")


def fail(msg: str) -> None:
    print(f"{RED}✗ {msg}{RESET}")


def check_file(path: Path) -> bool:
    print(f"\n{BOLD}=== {path.name} ==={RESET}")
    raw = path.read_bytes()
    if raw[:5] != b"%PDF-":
        warn("не PDF — сверка контрольных итогов поддержана только для PDF-выписок")
        return True

    bank = detect_pdf_bank(raw)
    if bank is None:
        fail("банк не опознан по содержимому файла")
        return False
    info(f"банк определён по содержимому: {bank}")

    transactions = parse_bank_pdf(raw, bank)
    if not transactions:
        reason = pdf_non_statement_reason(raw)
        if reason:
            warn(f"это {reason}, а не выписка операций — операций тут нет по определению")
            return True
        fail("операций не распознано, и это не справка — парсер не понял формат")
        return False
    info(f"распознано операций: {len(transactions)}")

    blank = [t for t in transactions if t["description"] in ("", "Операция")]
    if blank:
        warn(f"операций без описания: {len(blank)} — категоризатор по ним не отработает")

    result = reconcile_statement(raw, bank, transactions)
    if result["status"] == "ok":
        ok(result["message"])
        return True
    if result["status"] == "mismatch":
        fail(result["message"])
        return False
    warn("выписка не объявляет контрольных итогов — сверить нечем "
         f"(распознано: приход {result['parsed']['income']:.2f}, "
         f"расход {result['parsed']['expense']:.2f})")
    return True


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    results = []
    for arg in argv:
        path = Path(arg).expanduser()
        if not path.exists():
            fail(f"файл не найден: {path}")
            results.append(False)
            continue
        results.append(check_file(path))
    print()
    if all(results):
        ok(f"ИТОГ: сверка пройдена ({len(results)} файл(ов))")
        return 0
    fail(f"ИТОГ: проблемы в {results.count(False)} из {len(results)} файл(ов)")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
