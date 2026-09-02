/** GET /api/budgets/status отдаёт `list[dict[str, Any]]` (app/schemas/budget.py::BudgetStatus
 * + `id`, добавленный в crud.get_budget_status) — генератор OpenAPI не типизирует произвольный
 * dict строже, чем `Record<string, unknown>[]`. Локальный тип держит реальную форму ответа. */
export interface BudgetStatus {
  id: number;
  category: string;
  limit_amount: number;
  spent: number;
  pct: number;
  over: boolean;
}
