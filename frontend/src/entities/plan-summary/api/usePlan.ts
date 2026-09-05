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
      /* 🔴 Без каста. `as unknown as` здесь жил с тех пор, когда `CalculatePlanResult`
         вёлся руками и расходился со схемой: двойной каст выбрасывает сгенерированный
         тип и снимает сверку с контрактом целиком — TypeScript перестаёт видеть,
         что фронт ждёт полей, которых сервер не обещает (v8.31.1, дашборд в error
         boundary). С v8.40.0 тип реэкспортирует `PlanningCalculateResponse`, то есть
         SDK и так возвращает ровно его: каст стал не только опасным, но и лишним. */
      return data satisfies CalculatePlanResult;
    },
  });
}
