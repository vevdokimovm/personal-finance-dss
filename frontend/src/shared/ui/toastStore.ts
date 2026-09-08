import { create } from "zustand";

export type ToastVariant = "success" | "error";

export interface ToastAction {
  label: string;
  onClick: () => void;
}

export interface ToastItem {
  id: string;
  variant: ToastVariant;
  message: string;
  action?: ToastAction;
}

interface ToastState {
  toasts: ToastItem[];
  dismiss: (id: string) => void;
}

/** Тот же императивный паттерн, что useThemeStore.getState()/setState() (watchSystemTheme) —
 * toast() вызывается откуда угодно (обычно из onSuccess/onError мутации), не только из
 * компонента-подписчика, поэтому не хук. */
export const useToastStore = create<ToastState>()((set) => ({
  toasts: [],
  dismiss: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));

let counter = 0;

function push(variant: ToastVariant, message: string, action?: ToastAction): void {
  const id = `toast-${++counter}`;
  // Действие само закрывает тост сразу по клику (a11y-auditor, Батч 1) — иначе кнопка
  // «Вернуть» остаётся кликабельной до авто-скрытия, повторный клик может дёрнуть /restore
  // на уже восстановленной записи и показать ложную ошибку.
  const wrappedAction: ToastAction | undefined = action && {
    ...action,
    onClick: () => {
      action.onClick();
      useToastStore.getState().dismiss(id);
    },
  };
  useToastStore.setState((s) => ({
    toasts: [...s.toasts, { id, variant, message, action: wrappedAction }],
  }));
}

export const toast = {
  success: (message: string) => push("success", message),
  error: (message: string) => push("error", message),
  /** Удаление мягкое (P1.7) — действие «Вернуть» дёргает /restore. Вариант success, не error:
   * удаление прошло штатно, это не ошибка, просто отменяемое действие (тот же смысл, что
   * undo-toast в старой Jinja-версии, app.js). */
  undo: (message: string, onUndo: () => void) =>
    push("success", message, { label: "Вернуть", onClick: onUndo }),
  /** Ошибка, из которой есть выход. Нужна там, где «Повторить» бессмысленно: на 401
   * повтор возвращает 401 бесконечно, и единственный следующий шаг — вход заново.
   * Вариант `error`, а не `success`: это отказ, а не отменяемое действие. */
  errorWithAction: (message: string, label: string, onClick: () => void) =>
    push("error", message, { label, onClick }),
};
