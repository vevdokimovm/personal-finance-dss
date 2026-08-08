import { ListSkeleton, StatePanel, Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { useLiquidAssets } from "@entities/assets";
import { AssetRow } from "./ui/AssetRow";
import "./AssetsPage.css";

export function AssetsPage() {
  const query = useLiquidAssets();

  if (query.isLoading) {
    return (
      <main className="fp-assets">
        <h1>{t("Ликвидные активы")}</h1>
        <ListSkeleton rows={3} />
      </main>
    );
  }

  if (query.isError) {
    return (
      <main className="fp-assets">
        <h1>{t("Ликвидные активы")}</h1>
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
        <h1>{t("Ликвидные активы")}</h1>
        <StatePanel title={t("Активов пока нет")}>
          {t(
            "Свободный резерв и подушка безопасности — депозиты, накопительные счета, наличные, не привязанные к конкретной цели.",
          )}
        </StatePanel>
      </main>
    );
  }

  return (
    <main className="fp-assets">
      <h1>{t("Ликвидные активы")}</h1>
      <p className="fp-assets__lede">
        {t(
          "Свободный резерв и подушка безопасности. Деньги под конкретную цель — в разделе «Цели», не здесь.",
        )}
      </p>
      <ul className="fp-assets__list">
        {assets.map((asset) => (
          <AssetRow key={asset.id} asset={asset} />
        ))}
      </ul>
    </main>
  );
}
