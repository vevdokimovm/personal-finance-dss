"""Pydantic-схема ответа POST /planning/calculate (батч 0.3/0.4, Волна 0).

До этого батча эндпоинт был типизирован как dict[str, Any] — фронт вручную
дублировал форму в frontend/src/entities/plan-summary/model/types.ts с явной
пометкой в шапке файла: «когда бэкенд обзаведётся строгой Pydantic-схемой,
этот файл станет не нужен».

Глубина типизации намеренно неровная. `crisis_plan`/`surplus_plan` (модули
app/core/crisis.py, app/core/surplus.py) остаются dict[str, Any] — их форма
не менялась в этом батче, типизировать их попутно значило бы расширять
периметр батча без теста, который довёл бы эту типизацию до конца. Всё
остальное — контракт, который уже стабилен (Alternative, Explanation,
indicators) или который batch 0.3/0.4 добавляет (weighted_scores,
dominant_criterion, counterfactual) — типизировано строго.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.recommendation import BLRStatus


class DebtSchedule(BaseModel):
    """Помесячный график погашения долга — baseline vs накопительная лавина
    (ADR-016, канон v3.8.0, §10.5). Диагностика победившей альтернативы, не
    влияет на допустимость/ранжирование/кризисный режим."""

    baseline_months: int
    accelerated_months: int
    baseline_total_interest: float
    accelerated_total_interest: float
    interest_saved: float
    months_saved: int
    horizon_capped: bool
    negative_amortization: bool
    qualifying_debt_count: int


class PlanningIndicators(BaseModel):
    It: Optional[float] = None
    Et: Optional[float] = None
    SigmaP: Optional[float] = None
    CFt: Optional[float] = None
    Rt: float
    Lt: float
    Dt: float
    Bt: Optional[float] = None
    Bliq: Optional[float] = None
    BLR: Optional[float] = None
    BLR_status: Optional[BLRStatus] = None
    Dt_alert: bool = False
    # ADR-015 (канон v3.7.0): диагностика волатильности дохода — None, если
    # истории недостаточно. Влияет только на floor резерва, не на Rt/Dt.
    income_cv: Optional[float] = None
    # ADR-016 (канон v3.8.0): диагностика графика погашения победившей
    # альтернативы — None, если досрочки нет/некуда её девать. Только для
    # объяснения пользователю, не участвует в допустимости/ранжировании.
    debt_schedule: Optional[DebtSchedule] = None


class ClosedGoal(BaseModel):
    id: Optional[Any] = None
    name: str = ""
    amount: float = 0.0


class BliqPreallocation(BaseModel):
    closed_goals: List[ClosedGoal] = Field(default_factory=list)
    bliq_used: float = 0.0
    bliq_remaining: float = 0.0


class Weights(BaseModel):
    w_rt: float
    w_lt: float
    w_dt: float
    w_goals: float
    lt_target: float


class AlternativeScores(BaseModel):
    """Нормализованные (min-max) значения критериев внутри множества
    альтернатив — app/core/ranking.py::rank_alternatives."""

    Rt_norm: float
    Lt_norm: float
    Dt_norm: float
    Si_norm: float
    Lt_capped: float


class WeightedScores(BaseModel):
    """Вклад каждого критерия SAW в utility: w_x * x_norm (батч 0.3, Волна 0).

    Аддитивно к `scores` — сумма полей равна `utility` с точностью округления.
    Не влияет на ранжирование (сортировка по floor_level/utility не менялась).
    """

    Rt: float
    Lt: float
    Dt: float
    Si: float


class ObligationAllocationItem(BaseModel):
    id: Optional[Any] = None
    name: str = ""
    interest_rate: float = 0.0
    new_amount: float = 0.0
    new_payment: float = 0.0


class AvalanchePassed(BaseModel):
    name: str = ""
    interest_rate: float = 0.0
    paid_in: float = 0.0
    closed: bool = False
    payment_saved: float = 0.0


class AvalancheSkipped(BaseModel):
    name: str = ""
    interest_rate: float = 0.0


class AvalancheDetail(BaseModel):
    r_bench: float
    passed: List[AvalanchePassed] = Field(default_factory=list)
    skipped: List[AvalancheSkipped] = Field(default_factory=list)
    x_unused_to_goals: float = 0.0
    delta_payment: float = 0.0


class GoalBreakdownItem(BaseModel):
    id: Optional[Any] = None
    name: str = ""
    category: str = "material"
    weight: float = 1.0
    urgency: float = 1.0
    months_left: Optional[float] = None
    priority: float = 0.0
    remaining: float = 0.0
    share: float = 0.0
    amount: float = 0.0


class InvestmentTrancheSplit(BaseModel):
    deposits: float = 0.0
    bonds: float = 0.0
    equity: float = 0.0


class IISDeductionEstimate(BaseModel):
    """Реальный вычет ИИС типа А (ADR-017) — только когда применимо, иначе None."""

    eligible_amount: float
    deduction: float


class GrowthIllustrationPoint(BaseModel):
    """Иллюстрация сложного процента — НЕ прогноз, НЕ рекомендация инструмента."""

    rate: float
    years: int
    future_value: float


class InvestmentTranche(BaseModel):
    amount: float
    cushion_part: float = 0.0
    split: InvestmentTrancheSplit
    equity_share: float = 0.0
    note: str = ""
    iis_deduction_estimate: Optional[IISDeductionEstimate] = None
    growth_illustration: Optional[List[GrowthIllustrationPoint]] = None


class ExplanationDelta(BaseModel):
    Rt: float
    Lt: float
    Dt: float


class Counterfactual(BaseModel):
    """Что изменилось бы, чтобы победил другой вариант (батч 0.4, Волна 0).

    Сравнение с реально посчитанным следующим по рангу вариантом из того же
    ranked[] — не гипотетический сценарий. `dominant_criterion` здесь —
    служебный ключ (Rt/Lt/Dt/Si), как у существующего `delta`; человеческая
    формулировка — в `text` (без формульной нотации, FR-01/UX-02).
    """

    available: bool = False
    alternative_id: Optional[str] = None
    utility_gap: Optional[float] = None
    dominant_criterion: Optional[str] = None
    text: Optional[str] = None


class Explanation(BaseModel):
    gains: List[str] = Field(default_factory=list)
    costs: List[str] = Field(default_factory=list)
    insight: str = ""
    dominant_criterion: Optional[str] = None
    counterfactual: Optional[Counterfactual] = None
    delta: ExplanationDelta


class Alternative(BaseModel):
    id: str
    name: str = ""
    description: Optional[str] = None
    x_obligations: float = 0.0
    x_reserve: float = 0.0
    x_goals: float = 0.0
    x_remain: Optional[float] = None
    Rt_new: Optional[float] = None
    Lt_new: Optional[float] = None
    Dt_new: Optional[float] = None
    Si: Optional[float] = None
    x_obl_effective: Optional[float] = None
    x_obl_unused: Optional[float] = None
    x_reserve_effective: Optional[float] = None
    x_goals_unused: Optional[float] = None
    obligation_allocation: List[ObligationAllocationItem] = Field(default_factory=list)
    # goal_allocation ключи — id целей (app/core/goals_priority.py::calculate_goals_si
    # хранит их как есть, int из БД); JSON-объект допускает только строковые
    # ключи, поэтому приводим явно, а не полагаемся на неявную коэрсию Pydantic.
    goal_allocation: Dict[str, float] = Field(default_factory=dict)

    @field_validator("goal_allocation", mode="before")
    @classmethod
    def _stringify_goal_allocation_keys(cls, v: Any) -> Any:
        if isinstance(v, dict):
            return {str(k): val for k, val in v.items()}
        return v
    goal_breakdown: List[GoalBreakdownItem] = Field(default_factory=list)
    avalanche_detail: Optional[AvalancheDetail] = None
    investment_tranche: Optional[InvestmentTranche] = None
    scores: Optional[AlternativeScores] = None
    weighted_scores: Optional[WeightedScores] = None
    utility: Optional[float] = None
    floor_level: Optional[float] = None
    is_recommended: Optional[bool] = None
    # Только у альтернатив из filter_alternatives() (admissible + rejected);
    # у «сырых» из generate_alternatives ещё не проставлены.
    violations: List[str] = Field(default_factory=list)
    is_admissible: Optional[bool] = None
    # Только у top3 (explain_alternative вызывается только для них).
    explanation: Optional[Explanation] = None


class InputSummary(BaseModel):
    income: float
    expense: float
    bliq: float
    transactions_count: int
    obligations_count: int
    goals_count: int
    liquid_assets_count: int
    r_bench: float
    r_bench_source: str
    l_min: float
    risk_tolerance: int


class PlanningCalculateResponse(BaseModel):
    """Ответ POST /planning/calculate."""

    indicators: PlanningIndicators
    bliq_preallocation: BliqPreallocation
    risk_profile: str
    weights: Weights
    # Не типизированы в этом батче — см. докстринг модуля.
    crisis_plan: Optional[Dict[str, Any]] = None
    surplus_plan: Optional[Dict[str, Any]] = None
    alternatives_total: int
    admissible_count: int
    rejected_count: int
    top3: List[Alternative] = Field(default_factory=list)
    ranked: List[Alternative] = Field(default_factory=list)
    rejected: List[Alternative] = Field(default_factory=list)
    best: Optional[Alternative] = None
    input_summary: InputSummary
