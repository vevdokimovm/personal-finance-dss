import { useQuery } from "@tanstack/react-query";
import { keyRateEndpointApiPlanningKeyRateGet } from "@shared/api/generated";
import type { KeyRate } from "@shared/api/generated";

/**
 * GET /api/planning/key-rate — ключевая ставка ЦБ как ориентир для `r_bench`.
 *
 * Ставка меняется решениями ЦБ, а не по расписанию, но и не ежеминутно: держим час,
 * чтобы панель параметров не ходила за ней на каждый рендер.
 *
 * Схема заведена на бэкенде в этом же батче: поле называется `key_rate`, и рукописный
 * тип с полем `rate` дал бы `undefined` без предупреждения компилятора.
 */
export function useKeyRate() {
  return useQuery({
    queryKey: ["planning", "key-rate"],
    staleTime: 60 * 60 * 1000,
    queryFn: async () => {
      const { data } = await keyRateEndpointApiPlanningKeyRateGet({ throwOnError: true });
      return data as KeyRate;
    },
  });
}
