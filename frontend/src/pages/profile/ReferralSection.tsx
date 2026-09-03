import { useReferral } from "@entities/referral";
import { Button, CopyLinkField, ListSkeleton, StatePanel } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { pluralize } from "@shared/lib/i18n/plural";
import "./ReferralSection.css";

/**
 * Приглашение друзей — рефералка (P3.2/P3.4, ROADMAP §8.2 «ГЛАВНОЕ»).
 *
 * `/api/referral/me` существовал с кодом, ссылкой, счётчиком и достижениями — и не был
 * представлен на фронте ни строкой: ссылку было негде взять.
 *
 * Вторая, более злая половина: ссылка ведёт на `/register?ref=CODE`, но `RegisterPage`
 * параметр не читал и `referral_code` в запрос не клал. То есть приглашение
 * открывалось, регистрация проходила — и не засчитывалась никому. Тот же класс, что
 * мёртвый `/join` (v8.36.0), только незаметный: там человек упирался в пустоту, здесь
 * всё выглядит рабочим. Починено в этом же батче, гейт достижимости расширен на
 * «экран читает параметр», а не только «экран существует».
 *
 * Живёт секцией на профиле, а не отдельным экраном: это свойство аккаунта, а не
 * область финансовых данных, и девятый пункт в меню размывал бы навигацию ([IA-01]).
 * Цена решения названа прямо: обнаруживаемость низкая — вход один, и тот в профиле.
 * Контекстные входы (после позитивного события) — отдельная задача продукта, здесь
 * не изобретаются.
 *
 * 🔴 Про награды НИЧЕГО не обещается. `referral_milestones` отдаёт `reward=None` у всех
 * порогов — механики начисления не существует. Поэтому достижения показаны как счёт
 * приглашений, а не как витрина призов: пять пустых обещаний хуже, чем их отсутствие
 * ([IA-04] — тупиков не предлагаем).
 */

const INVITES: [string, string, string] = ["приглашение", "приглашения", "приглашений"];
const PEOPLE: [string, string, string] = ["человек", "человека", "человек"];

export function ReferralSection() {
  const referral = useReferral();
  const data = referral.data;
  const isEmpty = data ? data.invited_count === 0 : false;

  return (
    <section className="fp-profile__card fp-referral" aria-labelledby="fp-referral-title">
      <h2 className="fp-profile__section-title" id="fp-referral-title">
        {t("Приглашения друзей")}
      </h2>

      {referral.isLoading && <ListSkeleton rows={3} />}

      {referral.error && (
        <StatePanel
          // Не `alert`: сбой второстепенной секции не должен прерывать человека,
          // который пришёл на профиль за согласиями или почтой ([ST-06]).
          role="status"
          headingLevel={3}
          title={t("Не получилось загрузить приглашения")}
          action={
            <Button variant="ghost" onClick={() => referral.refetch()}>
              {t("Повторить")}
            </Button>
          }
        >
          {t("Проверьте соединение — ваш код при этом не изменился.")}
        </StatePanel>
      )}

      {data && (
        <>
          <p className="fp-referral__lede">
            {t(
              "Отправьте свою ссылку — тот, кто зарегистрируется по ней, будет засчитан " +
                "вам. Ссылка постоянная, её можно отправлять сколько угодно раз.",
            )}
          </p>

          {/* Подпись отличает эту ссылку от ссылки семейного доступа: та даёт человеку
              доступ к вашим финансам, эта — только регистрацию по вашему коду. Слово
              «приглашение» без уточнения означало бы в продукте две разные вещи. */}
          <CopyLinkField
            label={t("Ваша ссылка для друзей")}
            url={data.invite_url}
            variant="ghost"
          />

          {isEmpty ? (
            /* Нуль — самое частое состояние секции: он у каждого нового пользователя.
               Парадная лестница из пустых плашек и «осталось 1» при нуле выглядит как
               интерфейс, которому нечего сказать ([ST-03]). */
            <p className="fp-referral__empty">
              {t("Пока по вашей ссылке никто не пришёл. Отправьте её тому, кому FINPILOT пригодится.")}
            </p>
          ) : (
            <>
              <p className="fp-referral__count">
                <span className="fp-referral__count-value">{data.invited_count}</span>{" "}
                <span className="fp-referral__count-label">
                  {t("{word} пришли по вашей ссылке", {
                    word: pluralize(data.invited_count, PEOPLE).replace(
                      `${data.invited_count} `,
                      "",
                    ),
                  })}
                </span>
              </p>

              {data.next_milestone && (
                <p className="fp-referral__next">
                  {t("До «{title}» осталось {left}", {
                    title: data.next_milestone.title,
                    left: pluralize(data.next_milestone.remaining, INVITES),
                  })}
                </p>
              )}

              <h3 className="fp-referral__milestones-title">{t("Достижения")}</h3>
              <ul className="fp-referral__milestones" role="list">
                {data.milestones.map((milestone) => (
                  <li
                    key={milestone.threshold}
                    className={
                      milestone.reached
                        ? "fp-referral__milestone fp-referral__milestone--reached"
                        : "fp-referral__milestone"
                    }
                  >
                    <span className="fp-referral__milestone-title">{milestone.title}</span>
                    <span className="fp-referral__milestone-meta">
                      {/* Состояние словом, а не только рамкой ([A11Y-07]). */}
                      {milestone.reached
                        ? t("достигнуто · {n}", {
                            n: pluralize(milestone.threshold, INVITES),
                          })
                        : pluralize(milestone.threshold, INVITES)}
                    </span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </>
      )}
    </section>
  );
}
