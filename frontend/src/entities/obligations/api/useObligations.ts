import { useQuery } from "@tanstack/react-query";
import { getObligationsEndpointApiObligationsGet } from "@shared/api/generated";

/** GET /api/obligations — тот же паттерн, что usePlan/useForecast (entities/plan-summary).
 * Без `as unknown as` каста — ObligationResponse строго типизирован генератором. */
export function useObligations() {
  return useQuery({
    queryKey: ["obligations", "list"],
    queryFn: async () => {
      const { data } = await getObligationsEndpointApiObligationsGet({ throwOnError: true });
      return data;
    },
  });
}
