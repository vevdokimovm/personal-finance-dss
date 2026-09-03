import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  listPlanHistoryApiPlanningHistoryGet,
  savePlanHistoryApiPlanningHistoryPost,
  deletePlanHistoryApiPlanningHistorySnapshotIdDelete,
  restorePlanHistoryApiPlanningHistorySnapshotIdRestorePost,
} from "@shared/api/generated";
import type { PlanHistoryList } from "../model/types";

const HISTORY_KEY = ["plan-history"];

/** GET /api/planning/history — список сохранённых снимков плана (P2.6). */
export function usePlanHistory() {
  return useQuery({
    queryKey: HISTORY_KEY,
    queryFn: async () => {
      const { data } = await listPlanHistoryApiPlanningHistoryGet({ throwOnError: true });
      return data as PlanHistoryList;
    },
  });
}

function useInvalidateHistory() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: HISTORY_KEY });
}

/**
 * POST /api/planning/history — сохранить текущий план снимком.
 *
 * Бэкенд считает план заново по переданным параметрам, а не принимает готовый:
 * снимок обязан быть согласованным сам с собой, иначе в историю попало бы то, что
 * показал экран, а не то, что даёт модель.
 */
export function useSavePlanSnapshot() {
  const invalidate = useInvalidateHistory();
  return useMutation({
    mutationFn: async (body: { note?: string | null; risk_tolerance?: number | null }) => {
      const { data } = await savePlanHistoryApiPlanningHistoryPost({
        body,
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}

/** DELETE /api/planning/history/{id} — мягкое удаление снимка (обратимое). */
export function useDeletePlanSnapshot() {
  const invalidate = useInvalidateHistory();
  return useMutation({
    mutationFn: async (snapshotId: number) => {
      const { data } = await deletePlanHistoryApiPlanningHistorySnapshotIdDelete({
        path: { snapshot_id: snapshotId },
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}

/**
 * POST /api/planning/history/{id}/restore — отмена удаления.
 *
 * 🔴 Заведено в v8.38.0: удаление снимка было мягким и раньше, но вернуть его
 * пользователь не мог никак — единственная сущность продукта без отмены, при том что
 * у целей, активов, обязательств, операций и бюджетов она есть. Данные лежали в базе
 * и были недостижимы: «сказали, что удалили, а на деле спрятали».
 */
export function useRestorePlanSnapshot() {
  const invalidate = useInvalidateHistory();
  return useMutation({
    mutationFn: async (snapshotId: number) => {
      const { data } = await restorePlanHistoryApiPlanningHistorySnapshotIdRestorePost({
        path: { snapshot_id: snapshotId },
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}
