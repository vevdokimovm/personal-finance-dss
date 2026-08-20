import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  listGoalsApiGoalsGet,
  createGoalEndpointApiGoalsPost,
  updateGoalEndpointApiGoalsGoalIdPut,
  addGoalContributionEndpointApiGoalsGoalIdContributionsPost,
  deleteGoalEndpointApiGoalsGoalIdDelete,
  restoreGoalEndpointApiGoalsGoalIdRestorePost,
} from "@shared/api/generated";
import type { GoalContributionCreate, GoalCreate, GoalUpdate } from "@shared/api/generated";

const GOALS_QUERY_KEY = ["goals", "list"];

/** GET /api/goals — тот же паттерн, что usePlan/useForecast (entities/plan-summary).
 * Без `as unknown as` каста — GoalResponse строго типизирован генератором. */
export function useGoals() {
  return useQuery({
    queryKey: GOALS_QUERY_KEY,
    queryFn: async () => {
      const { data } = await listGoalsApiGoalsGet({ throwOnError: true });
      return data;
    },
  });
}

/** Мутации CRUD (Батч 2, ROADMAP §8.2) — паттерн из entities/obligations/api/useObligations.ts. */
function useInvalidateGoals() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: GOALS_QUERY_KEY });
}

export function useCreateGoal() {
  const invalidate = useInvalidateGoals();
  return useMutation({
    mutationFn: async (body: GoalCreate) => {
      const { data } = await createGoalEndpointApiGoalsPost({ body, throwOnError: true });
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useUpdateGoal() {
  const invalidate = useInvalidateGoals();
  return useMutation({
    mutationFn: async ({ id, body }: { id: number; body: GoalUpdate }) => {
      const { data } = await updateGoalEndpointApiGoalsGoalIdPut({
        path: { goal_id: id },
        body,
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}

/** «Внести прогресс» (владелец: отдельное действие, не общий edit — прибавляет
 * к current_amount, не перезаписывает; 409 для целей с linked_asset_id). */
export function useAddGoalContribution() {
  const invalidate = useInvalidateGoals();
  return useMutation({
    mutationFn: async ({ id, body }: { id: number; body: GoalContributionCreate }) => {
      const { data } = await addGoalContributionEndpointApiGoalsGoalIdContributionsPost({
        path: { goal_id: id },
        body,
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useDeleteGoal() {
  const invalidate = useInvalidateGoals();
  return useMutation({
    mutationFn: async (id: number) => {
      await deleteGoalEndpointApiGoalsGoalIdDelete({ path: { goal_id: id }, throwOnError: true });
      return id;
    },
    onSuccess: invalidate,
  });
}

export function useRestoreGoal() {
  const invalidate = useInvalidateGoals();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await restoreGoalEndpointApiGoalsGoalIdRestorePost({
        path: { goal_id: id },
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}
