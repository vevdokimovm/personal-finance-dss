import { useQuery } from "@tanstack/react-query";
import { myReferralApiReferralMeGet } from "@shared/api/generated";
import type { ReferralMe } from "../model/types";

/** GET /api/referral/me — код, ссылка-приглашение, счётчик и вехи. */
export function useReferral() {
  return useQuery({
    queryKey: ["referral", "me"],
    queryFn: async () => {
      const { data } = await myReferralApiReferralMeGet({ throwOnError: true });
      return data as ReferralMe;
    },
  });
}
