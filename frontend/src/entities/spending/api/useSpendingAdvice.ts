import { useQuery } from "@tanstack/react-query";
import { spendingAdviceEndpointApiPlanningSpendingAdviceGet } from "@shared/api/generated";
import type { SpendingAdviceResponse } from "../model/types";

/** Окно анализа по умолчанию — то же, что у бэкенда (`months: int = 6`).
 *
 * Дублируется здесь сознательно и проверяется тем, что ответ возвращает `months_window`:
 * подпись периода на экране берётся ИЗ ОТВЕТА, а не из этой константы, поэтому
 * расхождение с сервером видно сразу, а не превращается во вранье в заголовке. */
export const DEFAULT_MONTHS = 6;

/**
 * GET /api/planning/spending-advice — анализ трат по категориям (v8.54.0).
 *
 * Эндпоинт за периметром `_FIN`: при отозванном согласии на обработку финансовых
 * данных он отвечает 403. Ретрай на отказ сервера запрещён по той же причине, что
 * у колокольчика: три повтора превращаются в три отказа подряд, а повторять имеет
 * смысл сетевой сбой, а не осознанное «нет».
 */
export function useSpendingAdvice(months: number = DEFAULT_MONTHS) {
  return useQuery({
    queryKey: ["spending-advice", months],
    staleTime: 5 * 60 * 1000,
    retry: (count, error) => {
      const status = (error as { status?: number } | null)?.status;
      if (status === 403 || status === 401) return false;
      return count < 2;
    },
    queryFn: async () => {
      const { data } = await spendingAdviceEndpointApiPlanningSpendingAdviceGet({
        query: { months },
        throwOnError: true,
      });
      return data as SpendingAdviceResponse;
    },
  });
}
