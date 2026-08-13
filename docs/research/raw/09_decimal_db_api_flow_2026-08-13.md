# Поток денег через БД/сервисы/API — риск границы Decimal/float

**Тип материала:** внутренний код-ресёрч (Explore-агент читал файлы репозитория и живой
FastAPI TestClient), НЕ внешний источник в смысле README этого каталога — сохранено по
прямому указанию владельца, для непрерывности между сессиями/аккаунтами.

**Дата:** 2026-08-13. **Контекст:** тот же батч v8.19.2, что и файл 08 в этом каталоге.

**Задание агенту:** проверить, как деньги реально хранятся/сериализуются на всех
границах — БД (SQLAlchemy Numeric), CRUD, services (planning/report_pdf/plan_export/
statement_reconcile), API (Pydantic-схемы, openapi.json), и живым тестом подтвердить,
как FastAPI сериализует Decimal в response_model.

---

## Отчёт агента (дословно)

## Money Data Flow: float→Decimal Migration Investigation

### 1. Database Layer
`app/database/models.py` — money columns are `Numeric(14,2)` mapped as `Mapped[Decimal]`: `Transaction.amount` (184), `Obligation.amount/monthly_payment` (220,224), `Goal.target_amount/current_amount` (250,252), `Budget.limit_amount` (284), `LiquidAsset.amount` (322), `ObligationPayment.amount/remaining_after` (340,346), `GoalContribution.amount` (357), `FxRate.rate_to_usd` Numeric(18,8) (143), `UserPrefs.iis_contributed_this_year` Numeric(12,2) (385). Rate/ratio fields use `Numeric(6,4)` (interest_rate, savings_rate, l_min, r_bench) — also Decimal.

SQLAlchemy's `Numeric` returns `Decimal` in Python (verified: no `asdecimal=False` override anywhere; `grep asdecimal` → zero hits) — true for both SQLite and PostgreSQL dialects, so **DB reads already yield Decimal**, not float.

Non-money numeric fields deliberately stay `Float`: `PlanSnapshot`/`RunResult` engine-output columns (models.py:423-437, 506-515) — `rt, lt, dt, blr, x_obligations, u_score`, etc. These are dimensionless engine indicators, explicitly kept float per `money.py`'s design note (line 8-9).

`app/database/crud.py` already normalizes at write-time via `to_money()` (imported line 18): `create_transaction` (150), `bulk_create_transactions` (225), `create_budget` (333,339), `create_obligation` (648,651), `record_obligation_payment` (728,730), `create_goal` (766,767), `record_goal_contribution` (847), `create_liquid_asset` (879). `create_plan_snapshot` (1156-1197) converts engine indicators to float via local `_f()` helper (1172) — this writes to the Float-typed PlanSnapshot columns, separate concern from money Decimal columns.

### 2. Services Layer
`app/services/planning.py` — entry: obligations/goals arrive as **plain dicts** (not ORM), and `float(o.get(...))` is called pervasively (79, 117, 123, 172, 183-238) — so Decimal→float conversion happens *before* planning.py, at the route serialization boundary. Exit: `money()` wraps engine output at 244-282 (`It, Et, SigmaP, CFt, Rt, ..., BLR, bliq_used/remaining`).

`app/services/report_pdf.py` — local `_money(value: float) -> str` (35), consumes already-float report dict fields (83-108). No Decimal entry.

`app/services/plan_export.py` — same pattern, local `_money` at 157-179 formatting float dict values.

`app/services/statement_reconcile.py` — local `_money(value: float) -> str` (133), reconciles parsed bank-statement float sums against DB-derived floats (309-314).

**Key existing pattern**: `app/ingestion/engine.py` (adapter, INFRA-15/REFACTOR-04) is the one place that already documents and implements the exact conversion FINPILOT wants everywhere: docstring (5-11) states `FinancialSnapshot (Decimal, enum) → входные словари ядра (float, int) → результат run_planning → Recommendation (Decimal)`. It wraps `run_planning` (float-only core) with Decimal at both edges — a template for the migration.

### 3. API Layer
`app/api/routes_banks.py` — reads `Transaction.amount` (Decimal) directly at 127; converts via `to_money()` only for dedup-key comparison (145); accumulates `total_income/expense` as raw Decimal (153,155) without explicit float().

Pydantic schemas: **all money fields typed `float`**, confirmed via grep on routes_transactions/obligations/goals/fx/assets/budgets (only explicit hit: `routes_fx.py:32 amount: float`); `routes_planning.py:_serialize_obligations/_serialize_goals/_serialize_assets` (137-169) pass raw ORM `Decimal` values into dicts untyped, relying on downstream `float()` coercion in `app/core`.

`docs/api/openapi.json` — every money field (`amount, balance, payment, limit_amount, target/current_amount`, etc. — 39 matches across `AccountDTO, ObligationCreate/Response, GoalDTO/Response, TransactionDTO/Response, BudgetCreate/Response, LiquidAssetCreate/Response, ConvertRequest`...) is typed `"type": "number"`, no `string`/`anyOf`.

**Critical wire-format risk** (verified live): FastAPI's `response_model` serialization of a `Decimal` field emits **JSON string**, not number — `TestClient` roundtrip: `{"amount": Decimal("123.40")}` → `{"amount":"123.40"}` (string), whereas `fastapi.encoders.jsonable_encoder` alone converts Decimal→float (`123.4`, a number). Since FastAPI uses pydantic's native serializer for `response_model=...`, **naively switching a response schema field from `float` to `Decimal` will silently turn a JSON number into a JSON string**, breaking `.claude/agents/api-contract-guard.md` rule 3 ("числа не приходят строками") and any strict-typed frontend TS client. Response schemas must stay `float` (converted via `money()`) unless a custom Decimal serializer (`json_encoders`/`Annotated[Decimal, PlainSerializer(float)]`) is added.

### 4. Existing Decimal Usage (full inventory)
`app/core/money.py` (the helper itself); `app/database/models.py` (columns); `app/ingestion/models.py` (parallel Decimal domain model: `Account, Transaction, Debt, Goal, Recommendation`, RiskProfile — lines 38-108) + `app/ingestion/engine.py`, `contracts.py`, `providers/manual.py`, `providers/plaid.py`; `app/services/currency.py` (`CurrencyConverter`, Decimal FX math); `app/api/routes_b2b.py`, `app/api/routes_fx.py`, `app/api/routes_plaid.py` (consumers of ingestion Decimal types). **`app/core/*.py` proper (planning engine: alternatives, avalanche, crisis, surplus, investment, metrics, ranking, filtering, forecast, amortization, goals_priority) uses zero Decimal** — 100% float, entry/exit only via `money.py`'s `money()`/`to_money()`.

Tests: `tests/test_engine_golden.py` is explicitly a pre-migration characterization test — docstring states goal is to freeze a*/top3/ordering under the future Decimal conversion, with a penny-tolerance already built in (line 128). `tests/test_international.py` exercises the ingestion Decimal path directly. `tests/test_generator_v4.py` uses ad-hoc `Decimal(str(...))` for PDN assertions only.

### 5. Frontend Contract Risk
Confirmed via `.claude/agents/api-contract-guard.md`: frontend contract is generator-driven from `openapi.json` (rule 6, "ручные интерфейсы — находка") and explicitly forbids numbers arriving as strings (rule 3). Combined with the live FastAPI test above, this means the migration plan must convert Decimal→float strictly at the API response boundary (route/schema layer), never rely on default pydantic Decimal JSON serialization for money response fields.
