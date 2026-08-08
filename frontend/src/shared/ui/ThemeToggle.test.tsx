import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ThemeToggle } from "./ThemeToggle";
import { useThemeStore } from "@shared/lib/theme/useThemeStore";

beforeEach(() => {
  window.matchMedia = vi.fn().mockReturnValue({
    matches: false,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  });
  localStorage.clear();
  document.documentElement.removeAttribute("data-theme");
  useThemeStore.setState({ theme: "system", resolvedTheme: "dark" });
});

describe("ThemeToggle", () => {
  it("предлагает три варианта: светлая/тёмная/как в системе", () => {
    render(<ThemeToggle />);
    const select = screen.getByRole("combobox", { name: "Тема оформления" });
    const options = [...select.querySelectorAll("option")].map((o) => o.textContent);
    expect(options).toEqual(["Светлая", "Тёмная", "Как в системе"]);
  });

  it("выбор варианта переключает тему в сторе и на <html>", async () => {
    render(<ThemeToggle />);
    const select = screen.getByRole("combobox", { name: "Тема оформления" });
    await userEvent.selectOptions(select, "light");
    expect(useThemeStore.getState().theme).toBe("light");
    expect(document.documentElement.getAttribute("data-theme")).toBe("light");

    await userEvent.selectOptions(select, "dark");
    expect(useThemeStore.getState().theme).toBe("dark");
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });

  it("отражает текущее значение из стора", () => {
    useThemeStore.getState().setTheme("dark");
    render(<ThemeToggle />);
    const select = screen.getByRole("combobox", { name: "Тема оформления" }) as HTMLSelectElement;
    expect(select.value).toBe("dark");
  });
});
