import { useEffect } from "react";
import { createRootRoute, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { TooltipProvider, ToastProvider, ThemeToggle } from "@shared/ui";
import { watchSystemTheme } from "@shared/lib/theme/useThemeStore";
import { AuthTopbarLink } from "@widgets/auth-topbar";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  // Слушатель смены системной темы живёт, пока смонтирован рут — весь сеанс.
  useEffect(() => watchSystemTheme(), []);

  return (
    <TooltipProvider>
      <ToastProvider>
        <div className="fp-app-topbar">
          <AuthTopbarLink />
          <ThemeToggle />
        </div>
        <Outlet />
        {import.meta.env.DEV && <TanStackRouterDevtools position="bottom-right" />}
      </ToastProvider>
    </TooltipProvider>
  );
}
