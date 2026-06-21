from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ObligationCreate(BaseModel):
    name: str
    amount: float = Field(ge=0)
    interest_rate: float = Field(default=0.0, ge=0)
    term: int = 0
    monthly_payment: float = Field(ge=0)
    payment_day: int = 1
    comment: Optional[str] = None
    bank: Optional[str] = None
    type: str = "other"
    start_date: Optional[datetime] = None
    currency: str = "RUB"


class ObligationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    amount: float
    interest_rate: float
    term: int
    monthly_payment: float
    payment_day: int
    comment: Optional[str] = None
    bank: Optional[str] = None
    type: str = "other"
    start_date: Optional[datetime] = None
    is_active: bool = True
    closed_at: Optional[datetime] = None

    @computed_field
    @property
    def months_elapsed(self) -> int:
        """Сколько месяцев уже выплачивается (от даты взятия, не больше общего срока)."""
        if not self.start_date or self.term <= 0:
            return 0
        now = datetime.now()
        sd = self.start_date.replace(tzinfo=None) if self.start_date.tzinfo else self.start_date
        elapsed = (now.year - sd.year) * 12 + (now.month - sd.month)
        return max(0, min(self.term, elapsed))

    @computed_field
    @property
    def months_remaining(self) -> int:
        """Сколько месяцев осталось платить (общий срок минус пройденное)."""
        return max(0, self.term - self.months_elapsed)
