import { useQuery, useQueries } from "@tanstack/react-query";
import {
  experimentResultsEndpointApiAdminExperimentsKeyResultsGet,
  listExperimentsEndpointApiAdminExperimentsGet,
} from "@shared/api/generated";
import type { ExperimentResponse, ExperimentResults } from "../model/types";

/**
 * A/B-эксперименты владельца продукта (v8.49.0).
 *
 * Доступ — тот же признак `is_owner`, что у метрик: `require_admin` пропускает
 * владельца без ключа (v8.48.0). Запрос уходит только когда фронт уже знает, что
 * перед ним владелец, иначе каждый заход давал бы гарантированный 403.
 */
export function useExperiments(enabled = true) {
  return useQuery({
    queryKey: ["experiments", "list"],
    enabled,
    staleTime: 5 * 60 * 1000,
    queryFn: async () => {
      const { data } = await listExperimentsEndpointApiAdminExperimentsGet({
        throwOnError: true,
      });
      return data as ExperimentResponse[];
    },
  });
}

/**
 * Результаты по каждому эксперименту сразу.
 *
 * 🔴 `useQueries`, а не запрос на клик: экран отвечает на вопрос «какой эксперимент
 * что показал», и ради ответа по одному нужно было бы открыть каждый. Список
 * экспериментов у продукта короткий (единицы), поэтому цена приемлема; станет
 * длинным — здесь появится пагинация, а не ленивая загрузка по одному.
 */
export function useExperimentResults(keys: readonly string[], enabled = true) {
  return useQueries({
    queries: keys.map((key) => ({
      queryKey: ["experiments", "results", key],
      enabled,
      staleTime: 5 * 60 * 1000,
      queryFn: async () => {
        const { data } = await experimentResultsEndpointApiAdminExperimentsKeyResultsGet({
          path: { key },
          throwOnError: true,
        });
        return data as ExperimentResults;
      },
    })),
  });
}
