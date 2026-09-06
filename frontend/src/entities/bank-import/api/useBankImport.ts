import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listBanksApiBanksListGet, uploadStatementApiBanksUploadPost } from "@shared/api/generated";
import type { BankOption, StatementUploadResult } from "../model/types";

/** GET /api/banks/list — банки, для которых есть разбор выписки. */
export function useBanks() {
  return useQuery({
    queryKey: ["banks", "list"],
    // Список зашит в код бэкенда и меняется с релизами, а не в рантайме.
    staleTime: 60 * 60 * 1000,
    queryFn: async () => {
      const { data } = await listBanksApiBanksListGet({ throwOnError: true });
      return (data ?? []) as BankOption[];
    },
  });
}

/**
 * POST /api/banks/upload — импорт выписки.
 *
 * 🔴 Ошибка разбора приходит со статусом **200** и полем `status: "error"`: «файл не
 * распознан» — не сбой сервера, а результат работы. Поэтому `throwOnError` тут НЕ спасает,
 * и ветвление делает вызывающий по `result.status`. Молча считать любой 200 успехом
 * значило бы показать «импортировано» на нераспознанном файле.
 *
 * Импорт добавляет операции — инвалидируем всё, что от них считается: сами операции,
 * план, дашборд. Точечная инвалидация оставила бы экраны с устаревшими числами, и
 * человек решил бы, что импорт не сработал.
 */
export function useUploadStatement() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (args: { file: File; bankId: string }) => {
      const { data } = await uploadStatementApiBanksUploadPost({
        body: { file: args.file, bank_id: args.bankId },
        throwOnError: true,
      });
      return data as StatementUploadResult;
    },
    onSuccess: (result) => {
      if (result.status !== "success") return;
      void queryClient.invalidateQueries({ queryKey: ["transactions"] });
      void queryClient.invalidateQueries({ queryKey: ["plan"] });
      void queryClient.invalidateQueries({ queryKey: ["analysis"] });
    },
  });
}
