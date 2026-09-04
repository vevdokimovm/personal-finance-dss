import { useEffect } from "react";
import { createRootRoute, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { TooltipProvider, ToastProvider, ThemeToggle } from "@shared/ui";
import { LegalFooter } from "@widgets/legal-footer";
import { CookieBanner } from "@widgets/cookie-banner";
import { watchSystemTheme } from "@shared/lib/theme/useThemeStore";
import { t } from "@shared/lib/i18n/t";
import { AuthTopbarLink } from "@widgets/auth-topbar";
import { AppNav } from "@widgets/app-nav";
import { NotificationBell } from "@widgets/notification-bell";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  // Слушатель смены системной темы живёт, пока смонтирован рут — весь сеанс.
  useEffect(() => watchSystemTheme(), []);

  return (
    <TooltipProvider>
      <ToastProvider>
        {/* Обход повторяющегося блока (WCAG 2.4.1 Bypass Blocks, уровень A). До v8.31.0
            обходить было нечего: перед <main> стояли два контрола. С каркасом их девять,
            и они повторяются на КАЖДОМ экране — то есть цена появилась ровно вместе
            с навигацией, поэтому и закрывается тем же батчем. Ссылка первая в
            tab-порядке и видима только при фокусе (.fp-skip-link). */}
        <a href="#fp-main" className="fp-skip-link">
          {t("Перейти к содержимому")}
        </a>
        <header className="fp-app-header">
          <div className="fp-app-topbar">
            {/* Колокольчик прячется сам при отозванном согласии и у гостя (403/401),
                поэтому здесь без условий — состояние знает виджет, не раскладка. */}
            <NotificationBell />
            <AuthTopbarLink />
            <ThemeToggle />
          </div>
          {/* Каркас ниже топбара, а не внутри него: подписи полные ([CMP-03]) и на узком
              экране переносятся во вторую строку — рядом с email они бы жались. */}
          <AppNav />
        </header>
        {/* Якорь skip-link — здесь, а не на каждом <main>: их 38 в одиннадцати файлах
            (у экрана свой <main> в каждой ветке состояния), и новый экран молча остался
            бы без якоря. tabIndex={-1} нужен, чтобы фокус реально ушёл сюда, а не только
            прокрутка: без него скринридер продолжил бы читать с шапки. */}
        <div id="fp-main" tabIndex={-1} className="fp-main-anchor">
          <Outlet />
        </div>
        {/* Юр-контур — на КАЖДОЙ странице, включая гостевые (L6, L7): до входа оферту
            и политику читают чаще, чем после. Поэтому в корне, а не в экранах. */}
        <LegalFooter />
        <CookieBanner />
        {import.meta.env.DEV && <TanStackRouterDevtools position="bottom-right" />}
      </ToastProvider>
    </TooltipProvider>
  );
}
