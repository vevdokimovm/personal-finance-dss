from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BudgetCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=64)
    limit_amount: float = Field(..., gt=0)
    household_id: Optional[int] = None


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    limit_amount: float
    created_at: Optional[datetime] = None
    # 🔴 Общий доступ виден в ответе (v8.55.0). Без этого поля продукт принимал
    # `household_id` и отдавал ответ, по которому нельзя понять, стала ли запись
    # общей: человек думает «поделился», а проверить это нечем.
    household_id: Optional[int] = None


class BudgetStatus(BaseModel):
    """План-факт по одному категорийному бюджету (FR-22).

    🔴 `id` обязателен: по нему фронт правит и удаляет бюджет. Схема без него молча
    выбрасывала бы идентификатор при сериализации, и экран потерял бы редактирование —
    причём выглядело бы это дефектом фронта, а не контракта.
    """

    id: int
    category: str
    limit_amount: float
    spent: float
    pct: float
    over: bool
