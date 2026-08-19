import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getConsentsApiConsentsGet,
  grantApiConsentsConsentTypePost,
  withdrawApiConsentsConsentTypeDelete,
} from "@shared/api/generated";
import type { ConsentsMap, ConsentType } from "../model/types";

const CONSENTS_QUERY_KEY = ["consents", "state"];

/** GET /api/consents — тот же паттерн, что useObligations (entities/obligations). */
export function useConsents() {
  return useQuery({
    queryKey: CONSENTS_QUERY_KEY,
    queryFn: async () => {
      const { data } = await getConsentsApiConsentsGet({ throwOnError: true });
      return (data as { consents: ConsentsMap }).consents;
    },
  });
}

/** Согласие на финданные открывает разом шесть роутеров (_FIN, app/api/router.py) —
 * точечная инвалидация одного списка после выдачи/отзыва оставила бы остальные пять
 * в устаревшем error-состоянии. Согласие меняется редко — цена инвалидировать вообще
 * весь кэш ниже цены поддерживать точечный список ключей всех шести сущностей. */
function useInvalidateAfterConsentChange() {
  const queryClient = useQueryClient();
  return () => void queryClient.invalidateQueries();
}

export function useGrantConsent() {
  const invalidate = useInvalidateAfterConsentChange();
  return useMutation({
    mutationFn: async (consentType: ConsentType) => {
      const { data } = await grantApiConsentsConsentTypePost({
        path: { consent_type: consentType },
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useWithdrawConsent() {
  const invalidate = useInvalidateAfterConsentChange();
  return useMutation({
    mutationFn: async (consentType: ConsentType) => {
      await withdrawApiConsentsConsentTypeDelete({
        path: { consent_type: consentType },
        throwOnError: true,
      });
      return consentType;
    },
    onSuccess: invalidate,
  });
}
