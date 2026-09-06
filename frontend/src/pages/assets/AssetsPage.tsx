import { useRef, useState } from "react";
import { ListSkeleton, StatePanel, Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { getConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";
import { useLiquidAssets, type LiquidAsset } from "@entities/assets";
import { ConsentRequiredPanel } from "@entities/consents";
import { SessionExpiredPanel, isSessionExpired } from "@entities/auth";
import { AssetRow } from "./ui/AssetRow";
import { AssetForm } from "./ui/AssetForm";
import "./AssetsPage.css";

export function AssetsPage() {
  const query = useLiquidAssets();
  // undefined — модалка закрыта; null — создание; объект — правка этой записи.
  const [editing, setEditing] = useState<LiquidAsset | null | undefined>(undefined);
  const addButtonRef = useRef<HTMLButtonElement>(null);
  // Фокус после успешной выдачи согласия (a11y-auditor) — см. ObligationsPage.tsx.
  const headingRef = useRef<HTMLHeadingElement>(null);

  const addButton = (
    <Button ref={addButtonRef} variant="primary" onClick={() => setEditing(null)}>
      {t("Добавить актив")}
    </Button>
  );
  const modal = (
    // key форсирует remount при смене цели редактирования — см. тот же приём и обоснование
    // в ObligationsPage.tsx.
    <AssetForm
      key={editing?.id ?? "new"}
      open={editing !== undefined}
      onOpenChange={(open) => !open && setEditing(undefined)}
      asset={editing ?? undefined}
    />
  );

  if (query.isLoading) {
    return (
      <main className="fp-assets">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Ликвидные активы")}
        </h1>
        <ListSkeleton rows={3} />
      </main>
    );
  }

  if (query.isError) {
    /* 🔴 401 — истёкшая сессия, а не сбой связи (гипотеза 7). Кнопка «Повторить»
       на нём возвращала бы 401 бесконечно, а совет проверить интернет при работающем
       интернете уводит человека чинить не то. `JWT_TTL_HOURS = 168` и refresh-токена
       нет — событие регулярное. */
    if (isSessionExpired(query.error)) {
      return (
        <main className="fp-assets">
          <h1 ref={headingRef} tabIndex={-1}>
            {t("Ликвидные активы")}
          </h1>
          <SessionExpiredPanel redirectTo="/banks" />
        </main>
      );
    }
    const consentDetail = getConsentRequiredDetail(query.error);
    if (consentDetail) {
      return (
        <main className="fp-assets">
          <h1 ref={headingRef} tabIndex={-1}>
            {t("Ликвидные активы")}
          </h1>
          <ConsentRequiredPanel
            detail={consentDetail}
            onGranted={() => void query.refetch().then(() => headingRef.current?.focus())}
          />
        </main>
      );
    }
    return (
      <main className="fp-assets">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Ликвидные активы")}
        </h1>
        <StatePanel
          title={t("Не получилось загрузить активы")}
          role="alert"
          action={
            <Button variant="primary" onClick={() => void query.refetch()}>
              {t("Повторить")}
            </Button>
          }
        >
          {t("Проверьте соединение и попробуйте ещё раз. Если повторится — напишите в поддержку.")}
        </StatePanel>
      </main>
    );
  }

  const assets = query.data ?? [];

  if (assets.length === 0) {
    return (
      <main className="fp-assets">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Ликвидные активы")}
        </h1>
        <StatePanel title={t("Активов пока нет")} action={addButton}>
          {t(
            "Свободный резерв и подушка безопасности — депозиты, накопительные счета, наличные, не привязанные к конкретной цели.",
          )}
        </StatePanel>
        {modal}
      </main>
    );
  }

  return (
    <main className="fp-assets">
      <div className="fp-assets__head">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Ликвидные активы")}
        </h1>
        {addButton}
      </div>
      <p className="fp-assets__lede">
        {t(
          "Свободный резерв и подушка безопасности. Деньги под конкретную цель — в разделе «Цели», не здесь.",
        )}
      </p>
      <ul className="fp-assets__list">
        {assets.map((asset) => (
          <AssetRow
            key={asset.id}
            asset={asset}
            onEdit={() => setEditing(asset)}
            onDeleted={() => addButtonRef.current?.focus()}
          />
        ))}
      </ul>
      {modal}
    </main>
  );
}
