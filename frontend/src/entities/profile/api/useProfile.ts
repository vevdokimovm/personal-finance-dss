import { useQuery } from "@tanstack/react-query";
import { meApiAuthMeGet } from "@shared/api/generated";

/** 401 у /api/auth/me — ожидаемый, не сетевой сбой (в отличие от transactions/
 * obligations/goals/liquid-assets, этот эндпоинт требует аутентификации, гостевой
 * режим на него не распространяется — app/dependencies.py require_user). Не
 * задокументирован в openapi.json как отдельный response (там только 200,
 * security-схемы в файле нет вовсе — расхождение схемы с реальным поведением
 * бэкенда, см. CHANGELOG v8.7.0) — код полагается на исходники бэкенда,
 * не на контракт, это явно помечено здесь и не должно молчать после регенерации
 * снимка. */
/** 401 у `/auth/me`: гость либо истёкшая сессия.
 *
 * 🔴 `name` задан явно (v9.1.0): `isSessionExpired` в `entities/auth` распознаёт эту
 * ошибку по имени, а не через `instanceof`. Импорт из одной сущности в другую нарушил
 * бы слоистость FSD, а сравнение конструкторов ломается при дублировании модуля
 * в сборке. Имя переживает и то, и другое.
 */
export class NotAuthenticatedError extends Error {
  name = "NotAuthenticatedError";
}

/** Общий ключ кэша «кто я сейчас» — читает не только ProfilePage, но и топбар/auth-хуки
 * (entities/auth), которые инвалидируют его после логина/логаута. Один источник истины,
 * не строковый литерал в двух местах, который может разъехаться при правке. */
export const PROFILE_QUERY_KEY = ["profile", "me"] as const;

/** GET /api/auth/me — тот же паттерн, что usePlan/useForecast (entities/plan-summary),
 * но throwOnError:false вместо true: нужен доступ к response.status, чтобы отличить
 * 401 (нет смысла молча предлагать "Повторить" по кругу — a11y-auditor, Э4 партия 2,
 * P1: тупиковый цикл без объяснения причины для пользователей экранных дикторов) от
 * реального сетевого сбоя, где повтор осмыслен. */
export function useProfile() {
  return useQuery({
    queryKey: PROFILE_QUERY_KEY,
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
