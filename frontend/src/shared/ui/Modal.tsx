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
  /**
   * Куда вернуть фокус при закрытии. Нужен, когда модалка открывается ПРОПОМ `open`,
   * а не `Dialog.Trigger`: тогда Radix не знает элемента-триггера и уводит фокус
   * в `<body>` — клавиатурный пользователь теряет место на экране (WCAG 2.4.3).
   * Поймано e2e на подтверждении удаления снимка плана (v8.34.0); у форм CRUD-батчей
   * этой проблемы не было, потому что там модалка одна на экран и фокус возвращался
   * на единственную кнопку по случайности разметки, а не по устройству.
   */
  returnFocusTo?: () => HTMLElement | null;
  children: ReactNode;
}

/** Общая модалка форм создания/правки (Батч 1 CRUD-паритета, ROADMAP §8.2) —
 * первое применение `@radix-ui/react-dialog` в проекте (пакет стоял в package.json,
 * нигде не использовался, тот же случай, что `@radix-ui/react-toast` до Toast.tsx в v8.22.0).
 * Focus trap/Escape/клик по оверлею — из коробки Radix, не переизобретаем. */
export function Modal({
  open,
  onOpenChange,
  title,
  description,
  returnFocusTo,
  children,
}: ModalProps) {
  const contentRef = useRef<HTMLDivElement>(null);

  // Кнопка «×» стоит в DOM раньше формы (иначе не окажется в шапке визуально) — без этого
  // Radix ставит начальный фокус на первый фокусируемый элемент (a11y-auditor, Батч 1):
  // им была бы «×», а не первое поле формы. Ищем первое реальное поле и фокусируем его сами.
  function handleOpenAutoFocus(e: Event) {
    const field = contentRef.current?.querySelector<HTMLElement>("input, select, textarea");
    if (field) {
      e.preventDefault();
      field.focus();
      return;
    }
    // Полей нет — значит это диалог подтверждения. Дефолт Radix поставил бы фокус на
    // «×» (она первая в разметке), а APG для подтверждений требует наименее
    // разрушительного действия: у диалога удаления это «Отмена». Найдено a11y-аудитом.
    const firstAction = contentRef.current?.querySelector<HTMLElement>(
      "button:not(.fp-modal__close)",
    );
    if (firstAction) {
      e.preventDefault();
      firstAction.focus();
    }
  }

  // Возврат фокуса делается ИМЕННО здесь, а не в `onOpenChange` вызывающего кода:
  // Radix переносит фокус в своём `onCloseAutoFocus` уже ПОСЛЕ него, и внешний вызов
  // молча перетирается (проверено e2e — фокус оказывался в <body>).
  function handleCloseAutoFocus(e: Event) {
    const target = returnFocusTo?.();
    if (target) {
      e.preventDefault();
      target.focus();
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
          onCloseAutoFocus={handleCloseAutoFocus}
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
