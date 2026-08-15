import { useRef, type ReactNode } from "react";
import * as RadixDialog from "@radix-ui/react-dialog";
import "./Modal.css";

export interface ModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  /** Для скринридера — Radix предупреждает в dev-консоли без Description/aria-describedby
   * (WCAG 4.1.2). Форма внутри обычно не даёт готового краткого описания диалога, поэтому
   * визуально скрыт по умолчанию, а не дублирует title. */
  description: string;
  children: ReactNode;
}

/** Общая модалка форм создания/правки (Батч 1 CRUD-паритета, ROADMAP §8.2) —
 * первое применение `@radix-ui/react-dialog` в проекте (пакет стоял в package.json,
 * нигде не использовался, тот же случай, что `@radix-ui/react-toast` до Toast.tsx в v8.22.0).
 * Focus trap/Escape/клик по оверлею — из коробки Radix, не переизобретаем. */
export function Modal({ open, onOpenChange, title, description, children }: ModalProps) {
  const contentRef = useRef<HTMLDivElement>(null);

  // Кнопка «×» стоит в DOM раньше формы (иначе не окажется в шапке визуально) — без этого
  // Radix ставит начальный фокус на первый фокусируемый элемент (a11y-auditor, Батч 1):
  // им была бы «×», а не первое поле формы. Ищем первое реальное поле и фокусируем его сами.
  function handleOpenAutoFocus(e: Event) {
    const field = contentRef.current?.querySelector<HTMLElement>("input, select, textarea");
    if (field) {
      e.preventDefault();
      field.focus();
    }
  }

  return (
    <RadixDialog.Root open={open} onOpenChange={onOpenChange}>
      <RadixDialog.Portal>
        <RadixDialog.Overlay className="fp-modal-overlay" />
        <RadixDialog.Content
          ref={contentRef}
          className="fp-modal"
          onOpenAutoFocus={handleOpenAutoFocus}
        >
          <div className="fp-modal__head">
            <RadixDialog.Title className="fp-modal__title">{title}</RadixDialog.Title>
            <RadixDialog.Close className="fp-modal__close" aria-label="Закрыть">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                <path
                  d="M3 3L13 13M13 3L3 13"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
              </svg>
            </RadixDialog.Close>
          </div>
          <RadixDialog.Description className="sr-only">{description}</RadixDialog.Description>
          {children}
        </RadixDialog.Content>
      </RadixDialog.Portal>
    </RadixDialog.Root>
  );
}
