import { useId } from "react";
import { useThemeStore, type ThemePreference } from "@shared/lib/theme/useThemeStore";
import { t } from "@shared/lib/i18n/t";
import "./ThemeToggle.css";

const OPTIONS: { value: ThemePreference; label: string }[] = [
  { value: "light", label: t("Светлая") },
  { value: "dark", label: t("Тёмная") },
  { value: "system", label: t("Как в системе") },
];

// Нативный <select> — клавиатура и ARIA уже корректны в браузере, риск a11y
// ошибок ниже, чем у самодельной radiogroup (TOK-09, находки a11y-auditor Э3).
export function ThemeToggle() {
  const theme = useThemeStore((s) => s.theme);
  const setTheme = useThemeStore((s) => s.setTheme);
  const id = useId();

  return (
    <div className="fp-theme-toggle">
      <label htmlFor={id} className="sr-only">
        {t("Тема оформления")}
      </label>
      <select
        id={id}
        className="fp-theme-toggle__select"
        value={theme}
        onChange={(e) => setTheme(e.target.value as ThemePreference)}
      >
        {OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
