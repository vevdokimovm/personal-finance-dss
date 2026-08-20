import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getTransactionsEndpointApiTransactionsGet,
  createTransactionEndpointApiTransactionsPost,
  updateTransactionEndpointApiTransactionsTransactionIdPut,
  deleteTransactionEndpointApiTransactionsTransactionIdDelete,
  restoreTransactionEndpointApiTransactionsTransactionIdRestorePost,
} from "@shared/api/generated";
import type { TransactionCreate, TransactionUpdate } from "@shared/api/generated";

const TRANSACTIONS_QUERY_KEY = ["transactions", "list"];

/** GET /api/transactions — тот же паттерн, что usePlan/useForecast (entities/plan-summary).
 * Без `as unknown as` каста: в отличие от planning/* (бэк отдаёт dict[str, Any]),
 * TransactionResponse строго типизирован генератором (api-contract-guard). */
export function useTransactions() {
  return useQuery({
    queryKey: TRANSACTIONS_QUERY_KEY,
    queryFn: async () => {
      const { data } = await getTransactionsEndpointApiTransactionsGet({ throwOnError: true });
      return data;
    },
  });
}

/** Мутации CRUD (Батч 2, ROADMAP §8.2) — паттерн из entities/obligations/api/useObligations.ts. */
function useInvalidateTransactions() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: TRANSACTIONS_QUERY_KEY });
}

export function useCreateTransaction() {
  const invalidate = useInvalidateTransactions();
  return useMutation({
    mutationFn: async (body: TransactionCreate) => {
      const { data } = await createTransactionEndpointApiTransactionsPost({
        body,
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useUpdateTransaction() {
  const invalidate = useInvalidateTransactions();
  return useMutation({
    mutationFn: async ({ id, body }: { id: number; body: TransactionUpdate }) => {
      const { data } = await updateTransactionEndpointApiTransactionsTransactionIdPut({
        path: { transaction_id: id },
        body,
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useDeleteTransaction() {
  const invalidate = useInvalidateTransactions();
  return useMutation({
    mutationFn: async (id: number) => {
      await deleteTransactionEndpointApiTransactionsTransactionIdDelete({
        path: { transaction_id: id },
        throwOnError: true,
      });
      return id;
    },
    onSuccess: invalidate,
  });
}

export function useRestoreTransaction() {
  const invalidate = useInvalidateTransactions();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await restoreTransactionEndpointApiTransactionsTransactionIdRestorePost({
        path: { transaction_id: id },
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}
