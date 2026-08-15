import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getObligationsEndpointApiObligationsGet,
  createObligationEndpointApiObligationsPost,
  updateObligationEndpointApiObligationsObligationIdPut,
  deleteObligationEndpointApiObligationsObligationIdDelete,
  restoreObligationEndpointApiObligationsObligationIdRestorePost,
} from "@shared/api/generated";
import type { ObligationCreate, ObligationUpdate } from "@shared/api/generated";

const OBLIGATIONS_QUERY_KEY = ["obligations", "list"];

/** GET /api/obligations — тот же паттерн, что usePlan/useForecast (entities/plan-summary).
 * Без `as unknown as` каста — ObligationResponse строго типизирован генератором. */
export function useObligations() {
  return useQuery({
    queryKey: OBLIGATIONS_QUERY_KEY,
    queryFn: async () => {
      const { data } = await getObligationsEndpointApiObligationsGet({ throwOnError: true });
      return data;
    },
  });
}

/** Мутации CRUD (Батч 1, ROADMAP §8.2) — паттерн из entities/auth/api/useAuth.ts:
 * useMutation поверх сгенерированного SDK, инвалидация списка onSuccess. */
function useInvalidateObligations() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: OBLIGATIONS_QUERY_KEY });
}

export function useCreateObligation() {
  const invalidate = useInvalidateObligations();
  return useMutation({
    mutationFn: async (body: ObligationCreate) => {
      const { data } = await createObligationEndpointApiObligationsPost({
        body,
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useUpdateObligation() {
  const invalidate = useInvalidateObligations();
  return useMutation({
    mutationFn: async ({ id, body }: { id: number; body: ObligationUpdate }) => {
      const { data } = await updateObligationEndpointApiObligationsObligationIdPut({
        path: { obligation_id: id },
        body,
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useDeleteObligation() {
  const invalidate = useInvalidateObligations();
  return useMutation({
    mutationFn: async (id: number) => {
      await deleteObligationEndpointApiObligationsObligationIdDelete({
        path: { obligation_id: id },
        throwOnError: true,
      });
      return id;
    },
    onSuccess: invalidate,
  });
}

export function useRestoreObligation() {
  const invalidate = useInvalidateObligations();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await restoreObligationEndpointApiObligationsObligationIdRestorePost({
        path: { obligation_id: id },
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}
