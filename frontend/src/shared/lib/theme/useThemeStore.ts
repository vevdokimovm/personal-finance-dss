import { create } from "zustand";
import { persist } from "zustand/middleware";

export type ThemePreference = "light" | "dark" | "system";
export type ResolvedTheme = "light" | "dark";

function resolveSystemTheme(): ResolvedTheme {
  if (typeof window === "undefined" || !window.matchMedia) return "dark";
  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

function applyTheme(resolved: ResolvedTheme) {
  if (typeof document === "undefined") return;
  document.documentElement.setAttribute("data-theme", resolved);
}

interface ThemeState {
  theme: ThemePreference;
  resolvedTheme: ResolvedTheme;
  setTheme: (theme: ThemePreference) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: "system",
      resolvedTheme: resolveSystemTheme(),
      setTheme: (theme) => {
        const resolved = theme === "system" ? resolveSystemTheme() : theme;
        applyTheme(resolved);
        set({ theme, resolvedTheme: resolved });
      },
    }),
    {
      name: "fp-theme",
      onRehydrateStorage: () => (state) => {
        if (!state) return;
        const resolved = state.theme === "system" ? resolveSystemTheme() : state.theme;
        applyTheme(resolved);
        state.resolvedTheme = resolved;
      },
    },
  ),
);

/** Слушает смену системной темы ОС, пока выбор пользователя — "system".
 * Вызывать один раз на верхнем уровне приложения (RootLayout). */
export function watchSystemTheme(): () => void {
  if (typeof window === "undefined" || !window.matchMedia) return () => {};
  const mql = window.matchMedia("(prefers-color-scheme: light)");
  const onChange = () => {
    const { theme } = useThemeStore.getState();
    if (theme !== "system") return;
    const resolved = resolveSystemTheme();
    applyTheme(resolved);
    useThemeStore.setState({ resolvedTheme: resolved });
  };
  mql.addEventListener("change", onChange);
  return () => mql.removeEventListener("change", onChange);
}
