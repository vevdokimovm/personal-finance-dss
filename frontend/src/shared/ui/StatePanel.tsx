import type { ReactNode } from "react";
import "./StatePanel.css";

/** Общая карточка пустого/ошибочного состояния — перенесено из dashboard (Э3) сюда
 * при переносе Э4, чтобы не заводить второй копии на каждый новый экран.
 *
 * role по умолчанию — "status" (не пусто/не задано): пустой список — это тоже
 * смена состояния после завершения запроса (WCAG 4.1.3 Status Messages), без
 * роли screen reader не узнаёт, что загрузка кончилась и результатов нет, пока
 * не начнёт вручную сканировать страницу (a11y-auditor, Э4). "alert" — там, где
 * явно передан (ошибка, прерывает пользователя), "status" — вежливое объявление. */
export function StatePanel({
  title,
  action,
  role = "status",
  children,
}: {
  title: string;
  action?: ReactNode;
  role?: "alert" | "status";
  children: ReactNode;
}) {
  return (
    <div className="fp-state-panel" role={role}>
      <h2>{title}</h2>
      <p>{children}</p>
      {action}
    </div>
  );
}
