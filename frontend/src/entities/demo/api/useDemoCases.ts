import { useMutation, useQuery } from "@tanstack/react-query";
import {
  listCasesApiDemoCasesGet,
  loadDemoApiDemoLoadPost,
} from "@shared/api/generated";
import type { DemoCases } from "../model/types";

/**
 * GET /api/demo/cases — десять эталонных портретов с метаданными.
 *
 * Публичный и нужен именно гостю: это первый экран человека без своих данных.
 * `staleTime` большой — список меняется вместе с релизом, а не в рантайме.
 */
export function useDemoCases(enabled = true) {
  return useQuery({
    queryKey: ["demo", "cases"],
    enabled,
    staleTime: 60 * 60 * 1000,
    queryFn: async () => {
      const { data } = await listCasesApiDemoCasesGet({ throwOnError: true });
      return data as DemoCases;
    },
  });
}

/**
 * POST /api/demo/load — загрузить портрет в гостевую песочницу.
 *
 * 🔴 Только для гостя: сервер отдаёт 403 вошедшему, чтобы демо-данные не смешались
 * с настоящими (`routes_demo.py::load_demo`). Инвалидация кеша — на стороне вызывающего:
 * он знает, какие экраны показывает, и сбрасывать весь кеш отсюда было бы шире нужного.
 */
export function useLoadDemoCase() {
  return useMutation({
    mutationFn: async ({ caseKey }: { caseKey: string }) => {
      const { data } = await loadDemoApiDemoLoadPost({
        query: { case: caseKey },
        throwOnError: true,
      });
      return data;
    },
  });
}
