import { type ReactNode } from "react";
import * as RadixToast from "@radix-ui/react-toast";
import { useToastStore } from "./toastStore";
import "./Toast.css";

const SUCCESS_DURATION_MS = 4000;
// Undo-тост (действие «Вернуть») держим дольше обычного success — короткого окна не хватает,
// чтобы прочитать текст, понять, что произошло, и успеть нажать кнопку.
const UNDO_DURATION_MS = 8000;

/**
 * Единая система уведомлений (FB-04, `docs/ui_ux_design_standard.md`) — первое реальное
 * применение `@radix-ui/react-toast` в проекте (зависимость стояла в package.json, нигде не
 * использовалась). Успешные действия автоскрываются (FB-04 «неважные авто-скрываются»);
 * ошибки остаются, пока не закроют вручную — их читают, не теряют при быстром автозакрытии.
 *
 * `type="foreground"`/`"background"` — то, чем Radix решает assertive/polite озвучивание
 * (FB-05, WCAG 4.1.3): ошибка прерывает и объявляется сразу, статус успеха — вежливо.
 */
export function ToastProvider({ children }: { children: ReactNode }) {
  const toasts = useToastStore((s) => s.toasts);
  const dismiss = useToastStore((s) => s.dismiss);

  return (
    <RadixToast.Provider swipeDirection="right">
      {children}
      {toasts.map((t) => (
        <RadixToast.Root
          key={t.id}
          // Undo — не «успех» (действие только что отменило другое действие), отдельный
          // нейтральный вид, не зелёная полоса success (design-critic, Батч 1: два акцента —
          // полоса и кнопка «Вернуть» — на событии, которое не является подтверждением).
          className={`fp-toast fp-toast--${t.variant}${t.action ? " fp-toast--undo" : ""}`}
          type={t.variant === "error" ? "foreground" : "background"}
          duration={
            t.variant !== "success" ? Infinity : t.action ? UNDO_DURATION_MS : SUCCESS_DURATION_MS
          }
          onOpenChange={(open) => {
            if (!open) dismiss(t.id);
          }}
        >
          <RadixToast.Description>{t.message}</RadixToast.Description>
          {t.action && (
            <RadixToast.Action
              className="fp-toast__action"
              altText={t.action.label}
              onClick={t.action.onClick}
            >
              {t.action.label}
            </RadixToast.Action>
          )}
          <RadixToast.Close
            className="fp-toast__close"
            aria-label={
              t.variant === "error" ? "Закрыть уведомление об ошибке" : "Закрыть уведомление"
            }
          >
            ×
          </RadixToast.Close>
        </RadixToast.Root>
      ))}
      <RadixToast.Viewport className="fp-toast-viewport" />
    </RadixToast.Provider>
  );
}
