import { type ReactNode, useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// TanStack Query держит серверное состояние (docs/frontend_migration_plan.md §1.4).
// UI-состояние — React Context/local state; Zustand подключается только под конкретный
// кросс-компонентный кейс на Э3+ (YAGNI), не превентивно.
export function QueryProvider({ children }: { children: ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: 1,
          },
        },
      }),
  );

  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
