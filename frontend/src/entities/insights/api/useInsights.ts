import { useQuery } from "@tanstack/react-query";
import {
  funnelEndpointApiAnalyticsFunnelGet,
  overviewApiAnalyticsOverviewGet,
} from "@shared/api/generated";
import type { AnalyticsOverview, FunnelResponse } from "../model/types";

/**
 * Метрики продукта для владельца (v8.48.0).
 *
 * Доступ даёт признак `is_owner` на аккаунте — решение владельца 04.09.2026. Сервер
 * отдаёт 403 всем остальным, поэтому запрос уходит только когда фронт уже знает,
 * что перед ним владелец: иначе каждый заход на экран давал бы гарантированный отказ
 * в консоли и лишний запрос.
 */
export function useAnalyticsOverview(enabled = true, days = 30) {
  return useQuery({
    queryKey: ["insights", "overview", days],
    enabled,
    // Метрики меняются медленно, а запрос сканирует таблицу событий.
    staleTime: 5 * 60 * 1000,
    queryFn: async () => {
      const { data } = await overviewApiAnalyticsOverviewGet({
        query: { days },
        throwOnError: true,
      });
      return data as AnalyticsOverview;
    },
  });
}

export function useFunnel(enabled = true) {
  return useQuery({
    queryKey: ["insights", "funnel"],
    enabled,
    staleTime: 5 * 60 * 1000,
    queryFn: async () => {
      const { data } = await funnelEndpointApiAnalyticsFunnelGet({ throwOnError: true });
      return data as FunnelResponse;
    },
  });
}
