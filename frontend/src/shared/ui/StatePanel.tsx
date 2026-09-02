import type { ReactNode } from "react";
import "./StatePanel.css";

/** Общая карточка пустого/ошибочного состояния — перенесено из dashboard (Э3) сюда
 * при переносе Э4, чтобы не заводить второй копии на каждый новый экран.
 *
 * role по умолчанию — "status" (не пусто/не задано): пустой список — это тоже
 * смена состояния после завершения запроса (WCAG 4.1.3 Status Messages), без
 * роли screen reader не узнаёт, что загрузка кончилась и результатов нет, пока
 * не начнёт вручную сканировать страницу (a11y-auditor, Э4). "alert" — там, где
 * явно передан (ошибка, прерывает пользователя), "status" — вежливое объявление.
 *
 * headingLevel по умолчанию 2 — до Батча 3 CRUD-бюджета панель всегда стояла прямо
 * под h1 страницы (ObligationsPage/GoalsPage/...). BudgetsSection на дашборде — первый
 * случай, где панель вложена в СВОЮ секцию с h2 «Бюджеты по категориям» (design-critic:
 * h2 сразу за h2 без текста между ними режет контур документа) — там нужен h3. */
export function StatePanel({
  title,
  action,
  role = "status",
  headingLevel = 2,
  children,
}: {
  title: string;
  action?: ReactNode;
  role?: "alert" | "status";
  headingLevel?: 2 | 3;
  children: ReactNode;
}) {
  const Heading = headingLevel === 3 ? "h3" : "h2";
  return (
    <div className="fp-state-panel" role={role}>
      <Heading>{title}</Heading>
      <p>{children}</p>
      {action}
    </div>
  );
}
