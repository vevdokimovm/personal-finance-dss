import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  budgetStatusApiBudgetsStatusGet,
  addBudgetApiBudgetsPost,
  removeBudgetApiBudgetsBudgetIdDelete,
  restoreBudgetEndpointApiBudgetsBudgetIdRestorePost,
} from "@shared/api/generated";
import type { BudgetCreate } from "@shared/api/generated";

const BUDGETS_QUERY_KEY = ["budgets", "status"];

/** GET /api/budgets/status — план-факт (FR-22), не GET /api/budgets: строка списка
 * бюджета показывает потраченное и превышение, для этого нужны spent/pct/over,
 * которых голый BudgetResponse не содержит. */
export function useBudgetStatus() {
  return useQuery({
    queryKey: BUDGETS_QUERY_KEY,
    queryFn: async () => {
      const { data } = await budgetStatusApiBudgetsStatusGet({ throwOnError: true });
      return data ?? [];
    },
  });
}

function useInvalidateBudgets() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: BUDGETS_QUERY_KEY });
}

/** POST /api/budgets — upsert по `category` на бэке (FR-22, app/database/crud.py::create_budget):
 * существующая у владельца категория обновляет `limit_amount`, новая — создаёт строку.
 * Отдельного PUT/update нет — «правка лимита» это и есть повторный вызов той же мутации
 * с тем же `category`; BudgetForm поэтому блокирует изменение категории при правке. */
export function useCreateBudget() {
  const invalidate = useInvalidateBudgets();
  return useMutation({
    mutationFn: async (body: BudgetCreate) => {
      const { data } = await addBudgetApiBudgetsPost({ body, throwOnError: true });
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useDeleteBudget() {
  const invalidate = useInvalidateBudgets();
  return useMutation({
    mutationFn: async (id: number) => {
      await removeBudgetApiBudgetsBudgetIdDelete({
        path: { budget_id: id },
        throwOnError: true,
      });
      return id;
    },
    onSuccess: invalidate,
  });
}

export function useRestoreBudget() {
  const invalidate = useInvalidateBudgets();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await restoreBudgetEndpointApiBudgetsBudgetIdRestorePost({
        path: { budget_id: id },
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}
