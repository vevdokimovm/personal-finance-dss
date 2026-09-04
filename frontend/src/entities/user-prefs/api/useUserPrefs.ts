import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  readPrefsApiUserPrefsGet,
  patchPrefsApiUserPrefsPatch,
} from "@shared/api/generated";
import type { UserPrefsResponse, UserPrefsUpdate } from "../model/types";

const PREFS_KEY = ["user-prefs"];

/** GET /api/user-prefs — параметры расчёта: риск-профиль, Lmin, ставка, горизонт. */
export function useUserPrefs() {
  return useQuery({
    queryKey: PREFS_KEY,
    queryFn: async () => {
      const { data } = await readPrefsApiUserPrefsGet({ throwOnError: true });
      return data as UserPrefsResponse;
    },
  });
}

/**
 * PATCH /api/user-prefs — частичное обновление.
 *
 * 🔴 Инвалидируется НЕ только сам ответ prefs, но и план с прогнозом: они считаются
 * по этим параметрам. Без этого человек сменил бы риск-профиль и увидел прежнюю
 * рекомендацию — то есть решил бы, что настройка ни на что не влияет.
 */
export function useUpdateUserPrefs() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (patch: UserPrefsUpdate) => {
      const { data } = await patchPrefsApiUserPrefsPatch({ body: patch, throwOnError: true });
      return data as UserPrefsResponse;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: PREFS_KEY });
      // Префикс `["plan"]` накрывает и расчёт (`["plan", "calculate"]`), и прогноз
      // (`["plan", "forecast", horizon, rBench]`) — отдельный ключ прогноза не нужен.
      void queryClient.invalidateQueries({ queryKey: ["plan"] });
    },
  });
}
