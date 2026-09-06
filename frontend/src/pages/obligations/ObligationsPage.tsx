import { useRef, useState } from "react";
import { ListSkeleton, StatePanel, Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { getConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";
import { useObligations, type Obligation } from "@entities/obligations";
import { ConsentRequiredPanel } from "@entities/consents";
import { SessionExpiredPanel, isSessionExpired } from "@entities/auth";
import { ObligationRow } from "./ui/ObligationRow";
import { ObligationForm } from "./ui/ObligationForm";
import "./ObligationsPage.css";

export function ObligationsPage() {
  const query = useObligations();
  // undefined — модалка закрыта; null — создание; объект — правка этой записи.
  const [editing, setEditing] = useState<Obligation | null | undefined>(undefined);
  const addButtonRef = useRef<HTMLButtonElement>(null);
  // Фокус после успешной выдачи согласия (a11y-auditor, этот батч): ConsentRequiredPanel
  // размонтируется вместе с кнопкой, на которой стоял фокус, — без явного переноса фокус
  // проваливается в <body>. tabIndex={-1} — заголовок фокусируем программно, не таб-стопом.
  const headingRef = useRef<HTMLHeadingElement>(null);

  const addButton = (
    <Button ref={addButtonRef} variant="primary" onClick={() => setEditing(null)}>
      {t("Добавить обязательство")}
    </Button>
  );
  const modal = (
    // key форсирует remount при смене цели редактирования (или create→edit) — ObligationForm
    // держит поля в useState, инициализированном ИЗ obligation только при монтировании;
    // без key одна и та же форма переживает смену пропа и не сбрасывает значения (найдено
    // тестом при переключении между "новое" и "изменить").
    <ObligationForm
      key={editing?.id ?? "new"}
      open={editing !== undefined}
      onOpenChange={(open) => !open && setEditing(undefined)}
      obligation={editing ?? undefined}
    />
  );

  if (query.isLoading) {
    return (
      <main className="fp-obligations">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Кредиты и обязательства")}
        </h1>
        <ListSkeleton rows={4} />
      </main>
    );
  }

  if (query.isError) {
    /* 🔴 401 — истёкшая сессия, а не сбой связи (гипотеза 7). Кнопка «Повторить»
       на нём возвращала бы 401 бесконечно, а совет проверить интернет при работающем
       интернете уводит человека чинить не то. `JWT_TTL_HOURS = 168` и refresh-токена
       нет — событие регулярное. */
    if (isSessionExpired(query.error)) {
      return (
        <main className="fp-obligations">
          <h1 ref={headingRef} tabIndex={-1}>
            {t("Кредиты и обязательства")}
          </h1>
          <SessionExpiredPanel redirectTo="/obligations" />
        </main>
      );
    }
    const consentDetail = getConsentRequiredDetail(query.error);
    if (consentDetail) {
      return (
        <main className="fp-obligations">
          <h1 ref={headingRef} tabIndex={-1}>
            {t("Кредиты и обязательства")}
          </h1>
          <ConsentRequiredPanel
            detail={consentDetail}
            onGranted={() => void query.refetch().then(() => headingRef.current?.focus())}
          />
        </main>
      );
    }
    return (
      <main className="fp-obligations">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Кредиты и обязательства")}
        </h1>
        <StatePanel
          title={t("Не получилось загрузить обязательства")}
          role="alert"
          action={
            <Button variant="primary" onClick={() => void query.refetch()}>
              {t("Повторить")}
            </Button>
          }
        >
          {t("Проверьте соединение и попробуйте ещё раз. Если повторится — напишите в поддержку.")}
        </StatePanel>
      </main>
    );
  }

  const obligations = query.data ?? [];

  if (obligations.length === 0) {
    return (
      <main className="fp-obligations">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Кредиты и обязательства")}
        </h1>
        <StatePanel title={t("Обязательств нет")} action={addButton}>
          {t("Если есть кредиты или рассрочки — добавьте их, план распределения учтёт платежи.")}
        </StatePanel>
        {modal}
      </main>
    );
  }

  return (
    <main className="fp-obligations">
      <div className="fp-obligations__head">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Кредиты и обязательства")}
        </h1>
        {addButton}
      </div>
      <ul className="fp-obligations__list">
        {obligations.map((ob) => (
          <ObligationRow
            key={ob.id}
            obligation={ob}
            onEdit={() => setEditing(ob)}
            onDeleted={() => addButtonRef.current?.focus()}
          />
        ))}
      </ul>
      {modal}
    </main>
  );
}
