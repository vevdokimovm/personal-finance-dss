import { useQuery } from "@tanstack/react-query";
import { getTransactionsEndpointApiTransactionsGet } from "@shared/api/generated";

/** GET /api/transactions — тот же паттерн, что usePlan/useForecast (entities/plan-summary).
 * Без `as unknown as` каста: в отличие от planning/* (бэк отдаёт dict[str, Any]),
 * TransactionResponse строго типизирован генератором — каст глушил бы будущее
 * расхождение схемы вместо того, чтобы дать TS его поймать (api-contract-guard). */
export function useTransactions() {
  return useQuery({
    queryKey: ["transactions", "list"],
    queryFn: async () => {
      const { data } = await getTransactionsEndpointApiTransactionsGet({ throwOnError: true });
      return data;
    },
  });
}
