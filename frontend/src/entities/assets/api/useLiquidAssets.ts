import { useQuery } from "@tanstack/react-query";
import { listAssetsApiLiquidAssetsGet } from "@shared/api/generated";

/** GET /api/liquid-assets — тот же паттерн, что usePlan/useForecast (entities/plan-summary).
 * Без `as unknown as` каста — LiquidAssetResponse строго типизирован генератором (v8.6.0). */
export function useLiquidAssets() {
  return useQuery({
    queryKey: ["liquid-assets", "list"],
    queryFn: async () => {
      const { data } = await listAssetsApiLiquidAssetsGet({ throwOnError: true });
      return data;
    },
  });
}
