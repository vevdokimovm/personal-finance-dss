import { useQuery } from "@tanstack/react-query";
import { previewDemoApiDemoPreviewGet } from "@shared/api/generated";
import type { DemoPreview } from "../model/types";

/**
 * GET /api/demo/preview — расчёт портрета БЕЗ записи в базу.
 *
 * 🔴 Снимает необратимость выбора. `/demo/load` стирает всё, что гость успел внести,
 * мимо отмены — и до этого хука человек выбирал портрет вслепую, по абзацу прозы.
 * Теперь он сначала смотрит расчёт, потом решает, загружать ли.
 *
 * `enabled` управляется вызывающим: запрос уходит только когда карточку раскрыли.
 * Считать все десять портретов заранее — это десять прогонов Монте-Карло ради того,
 * что человек, скорее всего, не откроет.
 */
export function useDemoPreview(caseKey: string | null) {
  return useQuery({
    queryKey: ["demo", "preview", caseKey],
    enabled: caseKey !== null,
    // Расчёт детерминирован для одного портрета: пересчитывать при возврате незачем.
    staleTime: Infinity,
    queryFn: async () => {
      const { data } = await previewDemoApiDemoPreviewGet({
        query: { case: caseKey as string },
        throwOnError: true,
      });
      return data as DemoPreview;
    },
  });
}
