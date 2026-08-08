import { useEffect } from "react";
import { createRootRoute, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { TooltipProvider, ThemeToggle } from "@shared/ui";
import { watchSystemTheme } from "@shared/lib/theme/useThemeStore";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  // Слушатель смены системной темы живёт, пока смонтирован рут — весь сеанс.
  useEffect(() => watchSystemTheme(), []);

  return (
    <TooltipProvider>
      <div className="fp-app-topbar">
        <ThemeToggle />
      </div>
      <Outlet />
      {import.meta.env.DEV && <TanStackRouterDevtools position="bottom-right" />}
    </TooltipProvider>
  );
}
