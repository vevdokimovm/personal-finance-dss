import { StatePanel, Button, toast } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import type { ConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";
import { useGrantConsent } from "../api/useConsents";
import type { ConsentType } from "../model/types";
import "./ConsentRequiredPanel.css";

/** Рабочий минимум вместо полного экрана согласия L3 (ROADMAP §8.2): вместо
 * заглушки «проверьте соединение» на 403 гейта согласия — объяснение + кнопка
 * «Дать согласие» прямо там, где список упал. onGranted — обычно
 * `() => query.refetch()`: без этого пользователь даст согласие и всё равно
 * увидит старую заглушку, потому что список не перезапросится сам.
 *
 * Не рендерим `detail.message` дословно (design-critic, этот батч): серверный
 * текст оканчивается «...можно дать в настройках профиля» — верно там, где
 * этого текста показывается БЕЗ кнопки (инлайн-баннер формы, `extractErrorMessage`),
 * но здесь кнопка уже делает то же самое здесь и сейчас — отправлять пользователя
 * в другое место в момент, когда предлагаешь остаться, противоречиво. */
export function ConsentRequiredPanel({
  detail,
  onGranted,
  headingLevel,
}: {
  detail: ConsentRequiredDetail;
  onGranted: () => void;
  /** См. StatePanel — по умолчанию h2 (панель прямо под h1 страницы). */
  headingLevel?: 2 | 3;
}) {
  const grant = useGrantConsent();

  function handleGrant() {
    if (grant.isPending) return;
    grant.mutate(detail.consentType as ConsentType, {
      onSuccess: onGranted,
      onError: () => toast.error(t("Не получилось сохранить согласие. Попробуйте ещё раз.")),
    });
  }

  return (
    <StatePanel
      title={t("Нужно согласие на финансовые данные")}
      role="alert"
      headingLevel={headingLevel}
      action={
        <Button
          variant="primary"
          aria-disabled={grant.isPending}
          aria-busy={grant.isPending}
          onClick={handleGrant}
        >
          {grant.isPending ? t("Даём согласие…") : t("Дать согласие")}
        </Button>
      }
    >
      {t("Этот раздел работает с финансовыми данными — их обработка требует отдельного согласия.")}
      {detail.documentUrl && (
        // <span display:block>, не вложенный <p> — StatePanel уже оборачивает children
        // в свой <p>, вложенный <p> внутри <p> невалиден.
        <span className="fp-consent-panel__doc-link">
          <a href={detail.documentUrl} target="_blank" rel="noreferrer">
            {detail.documentTitle || t("Текст документа")}
            <span className="sr-only">{t(" (открывается в новой вкладке)")}</span>
          </a>
        </span>
      )}
    </StatePanel>
  );
}
