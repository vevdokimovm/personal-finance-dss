"""Pydantic-схемы ответа GET /planning/spending-advice (v8.54.0).

Эндпоинт живёт с мат-модели v3.0.0 и до этого батча был типизирован как
`dict[str, Any]`: в OpenAPI это пустой объект, генератор клиента выдаёт на него
`unknown`, и фронт вынужден дописывать форму руками. Так появились двойные касты,
снятые в v8.50.0, — правило вехи 8 «схема заводится на бэкенде ДО фронта»
выведено ровно из этого.

Поля повторяют dataclass-ы `app/core/spending_advice.py` один в один: сервисный
слой отдаёт их через `asdict`, и любое расхождение здесь означало бы срезанное
при сериализации поле — молча, без ошибки.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class CategoryStatsSchema(BaseModel):
    """Слой 1: статистика по категории за окно месяцев.

    Норма — медиана, разброс — MAD, аномалия — robust z-score: метод устойчив
    к выбросам, потому что один отпуск не должен переписывать норму «Транспорта».
    """

    category: str
    baseline: float
    mad: float
    current: float
    z_score: float
    freq_month: float
    avg_check: float
    share: float
    compressibility: float
    pain_score: float
    is_anomaly: bool
    months_observed: int


class SpendingAdviceSchema(BaseModel):
    """Слой 1: один совет по сокращению с уже посчитанной экономией."""

    category: str
    potential_saving: float
    reason: str
    current: float
    baseline: float
    message: str


class MerchantStatsSchema(BaseModel):
    """Слой 2: агрегат по мерчанту за текущий период (информационно)."""

    merchant: str
    total: float
    count: int
    avg_check: float
    category: str
    compressibility: float


class TemporalPatternSchema(BaseModel):
    """Слой 3-A: робастный тренд категории по завершённым месяцам."""

    category: str
    direction: str
    slope_abs: float
    slope_pct: float
    baseline: float
    months_observed: int
    message: str


class GoalImpactSchema(BaseModel):
    """Слой 3-B: на сколько экономия приближает цель.

    🔴 `months_to_deadline`, `eta_now` и `months_earlier` необязательны и означают
    разное: бессрочную цель, отсутствие пополнений вовсе и невозможность посчитать
    выигрыш. Схема, объявившая их обязательными, заставила бы фронт показать ноль
    там, где ответа нет, — а «до цели 0 месяцев» и «цель не пополняется» человек
    читает противоположным образом.
    """

    goal_name: str
    remaining: float
    months_to_deadline: Optional[float] = None
    current_monthly: float
    redirected_saving: float
    eta_now: Optional[float] = None
    eta_boosted: float
    months_earlier: Optional[float] = None
    on_track: bool
    message: str


class SpendingAdviceResponse(BaseModel):
    """Ответ GET /planning/spending-advice целиком.

    `months_with_data` возвращается вместе с окном намеренно: у нового пользователя
    данных меньше минимума модели (`MIN_MONTHS = 3`), и экран обязан объяснить это
    словами, а не показать пустые списки как поломку.
    """

    current_period: str
    months_window: int
    months_with_data: int
    advice: List[SpendingAdviceSchema] = Field(default_factory=list)
    stats: List[CategoryStatsSchema] = Field(default_factory=list)
    merchant_insights: List[MerchantStatsSchema] = Field(default_factory=list)
    temporal_patterns: List[TemporalPatternSchema] = Field(default_factory=list)
    goal_impact: List[GoalImpactSchema] = Field(default_factory=list)
    total_potential_saving: float
