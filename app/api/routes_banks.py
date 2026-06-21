from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.core.money import to_money
from app.database.crud import create_transaction
from app.database.models import Transaction
from app.dependencies import get_current_user_id, get_db
from app.services.bank_api import get_available_banks, sync_all_banks, sync_bank
from app.services.event_logger import log_event
from app.services.statement_parser import parse_bank_statement, parse_tinkoff_pdf

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
            "message": f"Файл больше {settings.MAX_UPLOAD_SIZE_MB} МБ — слишком большой для импорта.",
        }

    # PDF-выписка (Тинькофф из приложения отдаёт PDF) — отдельный парсер
    if raw[:5] == b"%PDF-":
        transactions = parse_tinkoff_pdf(raw)
        if not transactions:
            return {
                "status": "error",
                "message": "Не удалось распознать операции в PDF. Поддерживается PDF-выписка Тинькофф.",
            }
    else:
        # CSV: пробуем разные кодировки (Тинькофф часто использует cp1251)
        content = None
        for encoding in ['utf-8-sig', 'utf-8', 'cp1251', 'windows-1251', 'latin-1']:
            try:
                content = raw.decode(encoding)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue

        if content is None:
            return {"status": "error", "message": "Не удалось определить кодировку файла."}

        # Парсим
        transactions = parse_bank_statement(content, bank_id)

    if not transactions:
        return {
            "status": "error",
            "message": "Не удалось распознать транзакции. Проверьте формат файла и выбранный банк.",
        }

    # Сохраняем в БД батчами: один commit на тысячи строк строит гигантский
    # INSERT (риск таймаута воркера и лимита параметров СУБД). Коммитим порциями.
    from datetime import datetime
    BATCH_SIZE = 500
    added = 0
    total_income = 0.0
    total_expense = 0.0
    pending = 0

    # Дедупликация: ключи уже сохранённых операций пользователя — защита от повторного
    # импорта той же выписки. Загружаем один раз, проверяем в памяти (O(1) на строку).
    owner = Transaction.user_id == user_id if user_id else Transaction.user_id.is_(None)
    existing_keys = {
        (row.date, row.amount, row.type, row.description)
        for row in db.query(
            Transaction.date, Transaction.amount, Transaction.type, Transaction.description
        ).filter(owner, Transaction.is_deleted == False)  # noqa: E712
    }
    skipped_duplicates = 0

    for t in transactions:
        try:
            t_date = datetime.fromisoformat(t['date']) if isinstance(t['date'], str) else t['date']
            key = (t_date, to_money(t['amount']), t['type'], t.get('description'))
            if key in existing_keys:
                skipped_duplicates += 1
                continue
            existing_keys.add(key)
            create_transaction(
                db=db,
                amount=t['amount'],
                type=t['type'],
                date=t_date,
                is_synced=True,
                description=t.get('description'),
                mcc=t.get('mcc'),
                bank=bank_id,
                user_id=user_id,
                autocommit=False,
            )
            added += 1
            pending += 1
            if t['type'] == 'income':
                total_income += t['amount']
            else:
                total_expense += t['amount']
            if pending >= BATCH_SIZE:
                db.commit()
                pending = 0
        except Exception:
            continue

    db.commit()

    log_event("statement_imported", {
        "source": file.filename,
        "added_count": added,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
    })
    msg = f"Импортировано {added} операций из {file.filename}"
    if skipped_duplicates:
        msg += f", пропущено дублей: {skipped_duplicates}"
    return {
        "status": "success",
        "message": msg,
        "added_count": added,
        "skipped_duplicates": skipped_duplicates,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "filename": file.filename,
    }
