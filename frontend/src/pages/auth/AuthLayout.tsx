import type { ReactNode } from "react";
import "./AuthLayout.css";

/** Общий каркас для login/register/forgot-password/reset-password — узкая центрированная
 * карточка поверх токенов `panel.css` (та же визуальная плотность, что у остальных `.fp-panel`),
 * без нового визуального языка. Один `<h1>` на экран (не `<h2>`, как у `.fp-panel` внутри
 * дашборда — эти экраны самостоятельные, не виджеты внутри другого экрана). */
export function AuthLayout({
  title,
  lede,
  children,
  footer,
}: {
  title: string;
  lede?: string;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <main className="fp-auth">
      <div className="fp-auth__card">
        <h1>{title}</h1>
        {lede && <p className="fp-auth__lede">{lede}</p>}
        {children}
        {footer && <div className="fp-auth__footer">{footer}</div>}
      </div>
    </main>
  );
}
