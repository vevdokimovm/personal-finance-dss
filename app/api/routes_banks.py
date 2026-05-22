from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.database.crud import create_transaction
from app.services.bank_api import sync_bank, sync_all_banks, get_available_banks
from app.services.statement_parser import parse_bank_statement


router = APIRouter(prefix="/banks", tags=["Банки"])


@router.get("/list", summary="Список доступных банков")
def list_banks() -> list[dict[str, str]]:
    return get_available_banks()


@router.post("/sync/{bank_id}", summary="Симуляция синхронизации одного банка")
def trigger_single_sync(bank_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    return sync_bank(db=db, bank_id=bank_id)


@router.post("/sync", summary="Симуляция синхронизации всех банков")
def trigger_sync_all(db: Session = Depends(get_db)) -> dict[str, Any]:
    return sync_all_banks(db=db)


@router.post("/upload", summary="Загрузка банковской выписки (CSV)")
async def upload_statement(
    file: UploadFile = File(...),
    bank_id: str = Form(default="tinkoff"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Загружает CSV-выписку из банка и импортирует транзакции.
    Поддерживаемые банки: tinkoff, sber, alfa, vtb, raiffeisen, universal.
    """
    # Читаем файл
    raw = await file.read()
    
    # Пробуем разные кодировки (Тинькофф часто использует cp1251)
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
    
    # Сохраняем в БД
    added = 0
    total_income = 0.0
    total_expense = 0.0
    
    for t in transactions:
        try:
            from datetime import datetime
            t_date = datetime.fromisoformat(t['date']) if isinstance(t['date'], str) else t['date']
            
            create_transaction(
                db=db,
                amount=t['amount'],
                category=t['category'],
                type=t['type'],
                date=t_date,
                is_synced=True,
            )
            added += 1
            if t['type'] == 'income':
                total_income += t['amount']
            else:
                total_expense += t['amount']
        except Exception:
            continue
    
    return {
        "status": "success",
        "message": f"Импортировано {added} операций из {file.filename}",
        "added_count": added,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "filename": file.filename,
    }
