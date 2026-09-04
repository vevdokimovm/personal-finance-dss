import { useQuery } from "@tanstack/react-query";
import { legalDocumentsApiLegalDocumentsGet } from "@shared/api/generated";
import type { LegalDocuments } from "../model/types";

/**
 * GET /api/legal/documents — реестр документов и дисклеймер 39-ФЗ.
 *
 * Публичный эндпоинт: версии нужны и до входа (страница регистрации, футер у гостя).
 * `staleTime` большой — редакции документов меняются раз в месяцы, а запрос уходит
 * с каждой страницы.
 */
export function useLegalDocuments() {
  return useQuery({
    queryKey: ["legal", "documents"],
    staleTime: 60 * 60 * 1000,
    queryFn: async () => {
      const { data } = await legalDocumentsApiLegalDocumentsGet({ throwOnError: true });
      return data as LegalDocuments;
    },
  });
}
