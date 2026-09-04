import { useQuery } from "@tanstack/react-query";
import { legalDocumentContentApiLegalDocumentsSlugGet } from "@shared/api/generated";
import type { LegalDocumentContent } from "../model/types";

/**
 * GET /api/legal/documents/{slug} — ТЕКСТ юридического документа.
 *
 * Отдельно от `useLegalDocuments` (реестр): реестр висит в футере каждой страницы и
 * возит только метаданные, а текст нужен ровно на одном экране. Смешивать их значило бы
 * тянуть шесть документов целиком на каждой навигации ради ссылки из четырёх слов.
 *
 * Публичный: политику человек обязан прочитать ДО регистрации, иначе согласие
 * неинформированное. `staleTime` большой — редакции меняются раз в месяцы.
 */
export function useLegalDocument(slug: string | null) {
  return useQuery({
    queryKey: ["legal", "document", slug],
    // Пока slug не разрешён по реестру, запрашивать нечего: без этого ушёл бы
    // запрос с `null` в пути и вернул 404 на исправном адресе.
    enabled: slug !== null,
    staleTime: 60 * 60 * 1000,
    queryFn: async () => {
      const { data } = await legalDocumentContentApiLegalDocumentsSlugGet({
        path: { slug: slug as string },
        throwOnError: true,
      });
      return data as LegalDocumentContent;
    },
  });
}
