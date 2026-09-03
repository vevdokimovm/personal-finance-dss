import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CopyLinkField } from "./CopyLinkField";

const { toastError, toastSuccess } = vi.hoisted(() => ({
  toastError: vi.fn(),
  toastSuccess: vi.fn(),
}));

vi.mock("./toastStore", () => ({ toast: { error: toastError, success: toastSuccess } }));

beforeEach(() => vi.clearAllMocks());

describe("CopyLinkField", () => {
  it("подпись видима и связана с полем (FRM-02)", () => {
    render(<CopyLinkField label="Ваша ссылка" url="https://finpilot.ru/x" />);
    const input = screen.getByLabelText("Ваша ссылка");
    expect(input).toBeVisible();
    expect(input).toHaveValue("https://finpilot.ru/x");
  });

  it("копирует ссылку целиком", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    render(<CopyLinkField label="Ваша ссылка" url="https://finpilot.ru/x" />);
    await userEvent.click(screen.getByRole("button", { name: "Скопировать" }));
    expect(writeText).toHaveBeenCalledWith("https://finpilot.ru/x");
    expect(toastSuccess).toHaveBeenCalled();
  });

  /* Буфер недоступен на http, без разрешения и в старом браузере. Молчаливый провал
     выглядел бы как успешное копирование — человек отправил бы пустоту ([FB-01]). */
  it("отказ буфера не выдаётся за успех и выделяет ссылку за пользователя", async () => {
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockRejectedValue(new Error("denied")) },
    });
    render(<CopyLinkField label="Ваша ссылка" url="https://finpilot.ru/x" />);
    await userEvent.click(screen.getByRole("button", { name: "Скопировать" }));
    expect(toastError).toHaveBeenCalled();
    expect(toastSuccess).not.toHaveBeenCalled();
    expect(screen.getByLabelText("Ваша ссылка")).toHaveFocus();
  });

  it("поле только для чтения — ссылку нельзя испортить правкой", () => {
    render(<CopyLinkField label="Ваша ссылка" url="https://finpilot.ru/x" />);
    expect(screen.getByLabelText("Ваша ссылка")).toHaveAttribute("readonly");
  });
});
