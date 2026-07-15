from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.core.money import to_money
from app.database.crud import bulk_create_transactions
from app.database.models import Transaction
from app.dependencies import get_current_user_id, get_db
from app.services.bank_api import get_available_banks, sync_all_banks, sync_bank
from app.services.event_logger import log_event
from app.services.statement_parser import (
    decode_statement_bytes,
    detect_pdf_bank,
    parse_bank_pdf,
    parse_bank_statement,
    parse_xlsx,
    pdf_non_statement_reason,
)
from app.services.statement_reconcile import reconcile_statement

router = APIRouter(prefix="/banks", tags=["Банки"])


@router.get("/list", summary="Список доступных банков")
def list_banks() -> list[dict[str, str]]:
    return get_available_banks()


@router.post("/sync/{bank_id}", summary="Симуляция синхронизации одного банка")
def trigger_single_sync(
    bank_id: str,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, Any]:
    return sync_bank(db=db, bank_id=bank_id, user_id=user_id)


@router.post("/sync", summary="Симуляция синхронизации всех банков")
def trigger_sync_all(
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, Any]:
    return sync_all_banks(db=db, user_id=user_id)


@router.post("/upload", summary="Загрузка банковской выписки (CSV)")
async def upload_statement(
    file: UploadFile = File(...),
    bank_id: str = Form(default="tinkoff"),
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict[str, Any]:
    """
    Загружает CSV-выписку из банка и импортирует транзакции.
    Поддерживаемые банки: tinkoff, sber, alfa, vtb, raiffeisen, universal.
    """
    # Читаем файл
    raw = await file.read()

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(raw) > max_bytes:
        return {
            "status": "error",
            "message": f"Файл больше {settings.MAX_UPLOAD_SIZE_MB} МБ — "
                       "слишком большой для импорта.",
        }

    # PDF-выписка. Банк определяем по СОДЕРЖИМОМУ файла, а выбор в форме оставляем
    # запасным вариантом: ошибка в выпадающем списке отправляла выписку не в тот парсер
    # и давала пустой результат на совершенно исправном файле.
    reconciliation: dict[str, Any] | None = None
    detected_bank: str | None = None
    if raw[:5] == b"%PDF-":
        detected_bank = detect_pdf_bank(raw)
        effective_bank = detected_bank or bank_id
        transactions = parse_bank_pdf(raw, effective_bank)
        if transactions:
            reconciliation = reconcile_statement(raw, effective_bank, transactions)
        if not transactions:
            reason = pdf_non_statement_reason(raw)
            if reason:
                return {
                    "status": "error",
                    "message": f"Это {reason}, а не выписка операций. "
                               "Загрузите выписку по счёту с историей операций.",
                }
            return {
                "status": "error",
                "message": "Не удалось распознать операции в PDF. "
                           "Проверьте, что выбран правильный банк "
                           "(PDF поддерживаются для Тинькофф, ВТБ, Сбер).",
            }
    elif raw[:4] == b"PK\x03\x04":
        # XLSX — zip-контейнер; парсим теми же эвристиками, что и универсальный CSV
        transactions = parse_xlsx(raw, bank_id)
        if not transactions:
            return {
                "status": "error",
                "message": "Не удалось распознать операции в XLSX. "
                           "Проверьте, что в файле есть таблица с датой и суммой.",
            }
    else:
        # CSV/1C: декодер сам форсит cp1251 для 1C и перебирает кодировки для CSV.
        # `report` собирает статистику разбора: у CSV контрольных сумм обычно нет, и
        # единственная доступная проверка — не потеряли ли мы строки молча.
        content = decode_statement_bytes(raw)
        parse_report: dict = {}
        transactions = parse_bank_statement(content, bank_id, parse_report)
        if transactions:
            reconciliation = reconcile_statement(raw, bank_id, transactions, parse_report)

    if not transactions:
        return {
            "status": "error",
            "message": "Не удалось распознать транзакции. Проверьте формат файла и выбранный банк.",
        }

    # Дедупликация: ключи уже сохранённых операций пользователя — защита от повторного
    # импорта той же выписки. Загружаем один раз, проверяем в памяти (O(1) на строку).
    from datetime import datetime
    owner = Transaction.user_id == user_id if user_id else Transaction.user_id.is_(None)
    existing_keys = {
        (row.date, row.amount, row.type, row.description)
        for row in db.query(
            Transaction.date, Transaction.amount, Transaction.type, Transaction.description
        ).filter(owner, Transaction.is_deleted == False)  # noqa: E712
    }

    # Дедуп в памяти + подсчёт итогов. Вставка — bulk_create_transactions (без
    # поштучного _is_recurring-запроса на строку), чтобы большая выписка (12k+ строк)
    # не упиралась в таймаут воркера/прокси.
    deduped: list[dict] = []
    skipped_duplicates = 0
    total_income = 0.0
    total_expense = 0.0
    for t in transactions:
        try:
            t_date = datetime.fromisoformat(t['date']) if isinstance(t['date'], str) else t['date']
        except (ValueError, TypeError):
            continue
        key = (t_date, to_money(t['amount']), t['type'], t.get('description'))
        if key in existing_keys:
            skipped_duplicates += 1
            continue
        existing_keys.add(key)
        t['date'] = t_date
        deduped.append(t)
        if t['type'] == 'income':
            total_income += t['amount']
        else:
            total_expense += t['amount']

    added = bulk_create_transactions(db, deduped, user_id=user_id,
                                     bank=detected_bank or bank_id)

    log_event("statement_imported", {
        "source": file.filename,
        "added_count": added,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "bank_detected": detected_bank,
        "reconciliation": reconciliation["status"] if reconciliation else None,
    })
    msg = f"Импортировано {added} операций из {file.filename}"
    if skipped_duplicates:
        msg += f", пропущено дублей: {skipped_duplicates}"
    if detected_bank and detected_bank != bank_id:
        msg += f". Банк определён по файлу: {detected_bank}"
    return {
        "status": "success",
        "message": msg,
        "reconciliation": reconciliation,
        "added_count": added,
        "skipped_duplicates": skipped_duplicates,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "filename": file.filename,
    }
