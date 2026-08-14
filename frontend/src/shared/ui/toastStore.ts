import { create } from "zustand";

export type ToastVariant = "success" | "error";

export interface ToastItem {
  id: string;
  variant: ToastVariant;
  message: string;
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

function push(variant: ToastVariant, message: string): void {
  const id = `toast-${++counter}`;
  useToastStore.setState((s) => ({ toasts: [...s.toasts, { id, variant, message }] }));
}

export const toast = {
  success: (message: string) => push("success", message),
  error: (message: string) => push("error", message),
};
