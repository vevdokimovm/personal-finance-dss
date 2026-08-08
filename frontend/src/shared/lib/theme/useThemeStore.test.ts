import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useThemeStore, watchSystemTheme } from "./useThemeStore";

function mockMatchMedia(prefersLight: boolean) {
  const listeners: ((e: MediaQueryListEvent) => void)[] = [];
  const mql = {
    matches: prefersLight,
    media: "(prefers-color-scheme: light)",
    addEventListener: (_: string, cb: (e: MediaQueryListEvent) => void) => listeners.push(cb),
    removeEventListener: (_: string, cb: (e: MediaQueryListEvent) => void) => {
      const i = listeners.indexOf(cb);
      if (i >= 0) listeners.splice(i, 1);
    },
  };
  window.matchMedia = vi.fn().mockReturnValue(mql);
  return {
    fireChange: (matches: boolean) => {
      mql.matches = matches;
      listeners.forEach((cb) => cb({ matches } as MediaQueryListEvent));
    },
  };
}

describe("useThemeStore", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute("data-theme");
    useThemeStore.setState({ theme: "system", resolvedTheme: "dark" });
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("setTheme('light') выставляет data-theme на корне и в состоянии", () => {
    mockMatchMedia(false);
    useThemeStore.getState().setTheme("light");
    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
    expect(useThemeStore.getState().resolvedTheme).toBe("light");
    expect(useThemeStore.getState().theme).toBe("light");
  });

  it("setTheme('dark') выставляет data-theme=dark", () => {
    mockMatchMedia(true);
    useThemeStore.getState().setTheme("dark");
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
    expect(useThemeStore.getState().resolvedTheme).toBe("dark");
  });

  it("setTheme('system') резолвится по prefers-color-scheme", () => {
    mockMatchMedia(true); // ОС предпочитает светлую
    useThemeStore.getState().setTheme("system");
    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
    expect(useThemeStore.getState().theme).toBe("system");
    expect(useThemeStore.getState().resolvedTheme).toBe("light");
  });

  it("выбор сохраняется (persist) — переживает пересоздание состояния", () => {
    mockMatchMedia(false);
    useThemeStore.getState().setTheme("light");
    expect(localStorage.getItem("fp-theme")).toContain('"theme":"light"');
  });

  it("watchSystemTheme применяет смену ОС-темы, только пока выбран system", () => {
    const { fireChange } = mockMatchMedia(false);
    useThemeStore.getState().setTheme("system");
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");

    const stop = watchSystemTheme();
    fireChange(true);
    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
    stop();
  });

  it("watchSystemTheme НЕ трогает тему, если пользователь выбрал конкретную (не system)", () => {
    const { fireChange } = mockMatchMedia(false);
    useThemeStore.getState().setTheme("dark");
    const stop = watchSystemTheme();
    fireChange(true); // ОС переключилась на светлую, но выбор пользователя — dark
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
    stop();
  });
});
