import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { getForecastApiPlanningForecastPost } from "@shared/api/generated";
import type { ForecastResult } from "../model/types";

/** POST /api/planning/forecast — тот же паттерн, что usePlan: POST-чтение через useQuery.
 * `rBench` — необязательный сценарий «что если» (§8.4): без него бэкенд берёт реальную OCR.
 * `placeholderData: keepPreviousData` — при смене горизонта/ставки график остаётся на месте
 * (со старыми данными) до прихода нового ответа вместо схлопывания в скелетон/пустоту. */
export function useForecast(horizon = 12, rBench?: number) {
  return useQuery({
    queryKey: ["plan", "forecast", horizon, rBench ?? null],
    queryFn: async () => {
      const { data } = await getForecastApiPlanningForecastPost({
        body: { horizon, r_bench: rBench },
        throwOnError: true,
      });
      return data satisfies ForecastResult;
    },
    placeholderData: keepPreviousData,
  });
}
