import { useQuery } from "@tanstack/react-query";
import { listGoalsApiGoalsGet } from "@shared/api/generated";

/** GET /api/goals — тот же паттерн, что usePlan/useForecast (entities/plan-summary).
 * Без `as unknown as` каста — GoalResponse строго типизирован генератором. */
export function useGoals() {
  return useQuery({
    queryKey: ["goals", "list"],
    queryFn: async () => {
      const { data } = await listGoalsApiGoalsGet({ throwOnError: true });
      return data;
    },
  });
}
