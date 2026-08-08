import { useQuery } from "@tanstack/react-query";
import { getForecastApiPlanningForecastPost } from "@shared/api/generated";
import type { ForecastResult } from "../model/types";

/** POST /api/planning/forecast — тот же паттерн, что usePlan: POST-чтение через useQuery. */
export function useForecast(horizon = 12) {
  return useQuery({
    queryKey: ["plan", "forecast", horizon],
    queryFn: async () => {
      const { data } = await getForecastApiPlanningForecastPost({
        body: { horizon },
        throwOnError: true,
      });
      return data as unknown as ForecastResult;
    },
  });
}
