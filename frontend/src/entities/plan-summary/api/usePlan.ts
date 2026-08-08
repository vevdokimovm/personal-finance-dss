import { useQuery } from "@tanstack/react-query";
import { calculatePlanApiPlanningCalculatePost } from "@shared/api/generated";
import type { CalculatePlanResult } from "../model/types";

/**
 * POST /api/planning/calculate — не GET, но семантически чтение (пересчёт по уже сохранённым
 * данным пользователя, без побочных эффектов): оборачиваем в useQuery поверх сырой SDK-функции,
 * а не в сгенерированный useMutation, чтобы получить обычные isLoading/isError/data состояния
 * вместо ручного .mutate(). Тело пустое — риск-профиль и l_min берутся из настроек пользователя.
 */
export function usePlan() {
  return useQuery({
    queryKey: ["plan", "calculate"],
    queryFn: async () => {
      const { data } = await calculatePlanApiPlanningCalculatePost({
        body: {},
        throwOnError: true,
      });
      return data as unknown as CalculatePlanResult;
    },
  });
}
