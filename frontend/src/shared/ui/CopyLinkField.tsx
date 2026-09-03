import { useId, useRef } from "react";
import { Button } from "./Button";
import { toast } from "./toastStore";
import { t } from "@shared/lib/i18n/t";
import "./CopyLinkField.css";

/**
 * Поле со ссылкой и кнопкой «Скопировать».
 *
 * Вынесено в v8.37.0: разметка, стили и обработчик копирования существовали двумя
 * побайтовыми копиями — приглашение в семейный доступ и реферальная ссылка
 * ([CMP-01] запрещает дублирование компонента). Копии уже начали расходиться:
 * у одной подпись была видимой, у другой `sr-only`.
 *
 * Подпись видимая и постоянная ([FRM-02]): поле с адресом без подписи — коробка
 * с непонятным текстом, а единственная зацепка «кнопка справа» работает только
 * для зрячего пользователя, уже знающего, что тут происходит.
 */
export function CopyLinkField({
  label,
  url,
  hint,
  variant = "ghost",
}: {
  label: string;
  url: string;
  hint?: string;
  /** primary — когда копирование и есть главное действие экрана. */
  variant?: "primary" | "ghost";
}) {
  const id = useId();
  const inputRef = useRef<HTMLInputElement>(null);

  async function copy() {
    try {
      await navigator.clipboard.writeText(url);
      toast.success(t("Ссылка скопирована"));
    } catch {
      // Буфер недоступен (нет разрешения, http, старый браузер). Не притворяемся, что
      // скопировали, — и не ограничиваемся советом «выделите вручную», а сразу
      // выделяем: совет, который можно выполнить за пользователя, выполняется ([FB-01]).
      inputRef.current?.focus();
      inputRef.current?.select();
      toast.error(t("Не получилось скопировать. Ссылка выделена — нажмите Ctrl+C."));
    }
  }

  return (
    <div className="fp-copy-link">
      <label className="fp-copy-link__label" htmlFor={id}>
        {label}
      </label>
      <div className="fp-copy-link__row">
        <input
          id={id}
          ref={inputRef}
          className="fp-copy-link__url"
          readOnly
          value={url}
          onFocus={(e) => e.currentTarget.select()}
        />
        <Button variant={variant} onClick={() => void copy()}>
          {t("Скопировать")}
        </Button>
      </div>
      {hint && <p className="fp-copy-link__hint">{hint}</p>}
    </div>
  );
}
