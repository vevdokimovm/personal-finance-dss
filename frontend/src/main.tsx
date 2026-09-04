import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createRouter, RouterProvider } from "@tanstack/react-router";
import { QueryProvider } from "@app/providers";
import { configureApiClient } from "@shared/api/client";
import { routeTree } from "./routeTree.gen";
// 🔴 Шрифт грузится САМОХОСТОМ, а не с CDN Google Fonts, и это не вкусовщина:
// · рынок РФ — доступность fonts.googleapis.com не гарантирована, а шрифт не должен
//   зависеть от чужого домена;
// · веха 9 требует CSP без сторонних источников — внешний шрифт пришлось бы разрешать;
// · один запрос к своему домену вместо двух к чужому (css + woff2).
// Вариативный woff2 несёт весь диапазон начертаний одним файлом, кириллица включена.
//
// До v8.39.0 токен `--font-body: "Manrope", …` существовал, а сам шрифт НЕ загружался
// ниоткуда: весь SPA рендерился системным шрифтом, то есть дизайн-система обещала
// гарнитуру, которой в продукте не было (найдено design-critic ещё в v8.10.0).
import "@fontsource-variable/manrope";
import "@app/styles/global.css";

configureApiClient();

const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

const rootEl = document.getElementById("root");
if (!rootEl) throw new Error("#root не найден в index.html");

createRoot(rootEl).render(
  <StrictMode>
    <QueryProvider>
      <RouterProvider router={router} />
    </QueryProvider>
  </StrictMode>,
);
