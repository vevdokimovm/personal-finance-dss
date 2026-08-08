import { useQuery } from "@tanstack/react-query";
import { meApiAuthMeGet } from "@shared/api/generated";

/** 401 у /api/auth/me — ожидаемый, не сетевой сбой (в отличие от transactions/
 * obligations/goals/liquid-assets, этот эндпоинт требует аутентификации, гостевой
 * режим на него не распространяется — app/dependencies.py require_user). Не
 * задокументирован в openapi.json как отдельный response (там только 200,
 * security-схемы в файле нет вовсе — расхождение схемы с реальным поведением
 * бэкенда, см. WATCHLOG/CHANGELOG v8.7.0) — код полагается на исходники бэкенда,
 * не на контракт, это явно помечено здесь и не должно молчать после регенерации
 * снимка. */
export class NotAuthenticatedError extends Error {}

/** GET /api/auth/me — тот же паттерн, что usePlan/useForecast (entities/plan-summary),
 * но throwOnError:false вместо true: нужен доступ к response.status, чтобы отличить
 * 401 (нет смысла молча предлагать "Повторить" по кругу — a11y-auditor, Э4 партия 2,
 * P1: тупиковый цикл без объяснения причины для пользователей экранных дикторов) от
 * реального сетевого сбоя, где повтор осмыслен. */
export function useProfile() {
  return useQuery({
    queryKey: ["profile", "me"],
    queryFn: async () => {
      const { data, error, response } = await meApiAuthMeGet({ throwOnError: false });
      if (error) {
        // response может быть undefined при обрыве сети до получения ответа
        // (fetch кидает раньше, чем появляется Response) — тогда это точно не 401.
        if (response?.status === 401) throw new NotAuthenticatedError();
        throw error;
      }
      return data;
    },
  });
}
