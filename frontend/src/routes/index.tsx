import { createFileRoute } from "@tanstack/react-router";
import { Button, Tooltip } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";

export const Route = createFileRoute("/")({
  component: HomePlaceholder,
});

// Экраны собираются в Э3 (docs/frontend_milestone8_plan.md) — auth-флоу, затем dashboard.
// Здесь — минимальное доказательство, что каркас (роутер/токены/примитивы/API-клиент) работает.
function HomePlaceholder() {
  return (
    <main
      style={{
        maxWidth: "var(--content-max)",
        margin: "0 auto",
        padding: "var(--sp-7) var(--sp-5)",
      }}
    >
      <h1 style={{ fontSize: "var(--fs-2xl)", fontWeight: 800, margin: "0 0 var(--sp-3)" }}>
        {t("FINPILOT — каркас вехи 8")}
      </h1>
      <p style={{ color: "var(--c-text2)", fontSize: "var(--fs-md)", margin: "0 0 var(--sp-6)" }}>
        {t("Экраны ещё не собраны — см. docs/frontend_milestone8_plan.md, этап Э3.")}
      </p>
      <Tooltip label={t("Токены направления «Спокойный», docs/ui_directions/calm/")}>
        <Button variant="primary">{t("Проверка каркаса")}</Button>
      </Tooltip>
    </main>
  );
}
