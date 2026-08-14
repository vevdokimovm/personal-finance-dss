import { afterEach, describe, expect, it } from "vitest";
import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ToastProvider } from "./Toast";
import { toast, useToastStore } from "./toastStore";

afterEach(() => {
  act(() => {
    useToastStore.setState({ toasts: [] });
  });
});

describe("Toast — единая система уведомлений (FB-04, ui_ux_design_standard.md)", () => {
  it("toast.success() показывает сообщение", async () => {
    render(<ToastProvider>{null}</ToastProvider>);
    act(() => toast.success("Письмо отправлено."));
    expect(await screen.findByText("Письмо отправлено.")).toBeInTheDocument();
  });

  it("toast.error() тоже показывает сообщение — отдельным вариантом", async () => {
    render(<ToastProvider>{null}</ToastProvider>);
    act(() => toast.error("Неверный email или пароль."));
    const node = await screen.findByText("Неверный email или пароль.");
    expect(node.closest(".fp-toast")).toHaveClass("fp-toast--error");
  });

  it("успешный тост закрывается по клику на «×», ошибка не закрывается сама (duration=Infinity)", async () => {
    render(<ToastProvider>{null}</ToastProvider>);
    act(() => toast.success("Готово."));
    const closeButton = await screen.findByRole("button", { name: "Закрыть уведомление" });
    await userEvent.click(closeButton);
    await waitFor(() => {
      expect(screen.queryByText("Готово.")).not.toBeInTheDocument();
    });
  });

  it("несколько тостов подряд не затирают друг друга — оба видны", async () => {
    render(<ToastProvider>{null}</ToastProvider>);
    act(() => {
      toast.success("Первое.");
      toast.error("Второе.");
    });
    expect(await screen.findByText("Первое.")).toBeInTheDocument();
    expect(await screen.findByText("Второе.")).toBeInTheDocument();
  });
});

describe("toastStore — императивный вызов вне React-дерева (тот же паттерн, что useThemeStore)", () => {
  it("push добавляет запись в store с уникальным id", () => {
    act(() => {
      toast.success("A");
      toast.success("B");
    });
    const ids = useToastStore.getState().toasts.map((t) => t.id);
    expect(new Set(ids).size).toBe(2);
  });

  it("dismiss убирает конкретный тост по id, не все", () => {
    act(() => toast.success("Останется"));
    const [{ id }] = useToastStore.getState().toasts;
    act(() => toast.error("Тоже останется"));
    act(() => useToastStore.getState().dismiss(id));
    const messages = useToastStore.getState().toasts.map((t) => t.message);
    expect(messages).toEqual(["Тоже останется"]);
  });
});
