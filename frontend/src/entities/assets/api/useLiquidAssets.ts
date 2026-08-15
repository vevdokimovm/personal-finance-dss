import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  listAssetsApiLiquidAssetsGet,
  addAssetApiLiquidAssetsPost,
  updateAssetApiLiquidAssetsAssetIdPut,
  removeAssetApiLiquidAssetsAssetIdDelete,
  restoreAssetApiLiquidAssetsAssetIdRestorePost,
} from "@shared/api/generated";
import type { LiquidAssetCreate, LiquidAssetUpdate } from "@shared/api/generated";

const ASSETS_QUERY_KEY = ["liquid-assets", "list"];

/** GET /api/liquid-assets — тот же паттерн, что usePlan/useForecast (entities/plan-summary).
 * Без `as unknown as` каста — LiquidAssetResponse строго типизирован генератором (v8.6.0). */
export function useLiquidAssets() {
  return useQuery({
    queryKey: ASSETS_QUERY_KEY,
    queryFn: async () => {
      const { data } = await listAssetsApiLiquidAssetsGet({ throwOnError: true });
      return data;
    },
  });
}

/** Мутации CRUD (Батч 1, ROADMAP §8.2) — паттерн из entities/auth/api/useAuth.ts. */
function useInvalidateAssets() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: ASSETS_QUERY_KEY });
}

export function useCreateAsset() {
  const invalidate = useInvalidateAssets();
  return useMutation({
    mutationFn: async (body: LiquidAssetCreate) => {
      const { data } = await addAssetApiLiquidAssetsPost({ body, throwOnError: true });
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useUpdateAsset() {
  const invalidate = useInvalidateAssets();
  return useMutation({
    mutationFn: async ({ id, body }: { id: number; body: LiquidAssetUpdate }) => {
      const { data } = await updateAssetApiLiquidAssetsAssetIdPut({
        path: { asset_id: id },
        body,
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useDeleteAsset() {
  const invalidate = useInvalidateAssets();
  return useMutation({
    mutationFn: async (id: number) => {
      await removeAssetApiLiquidAssetsAssetIdDelete({ path: { asset_id: id }, throwOnError: true });
      return id;
    },
    onSuccess: invalidate,
  });
}

export function useRestoreAsset() {
  const invalidate = useInvalidateAssets();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await restoreAssetApiLiquidAssetsAssetIdRestorePost({
        path: { asset_id: id },
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}
