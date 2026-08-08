import { defineConfig } from "@hey-api/openapi-ts";

// Генерирует SDK + Zod-подобные типы + хуки TanStack Query из контракта бэка.
// Клиент не пишем руками (docs/frontend_milestone8_plan.md, Шаг 2). Запуск: npm run generate:client.
export default defineConfig({
  input: "../docs/api/openapi.json",
  output: {
    path: "src/shared/api/generated",
    clean: true,
  },
  plugins: [
    "@hey-api/client-fetch",
    "@hey-api/typescript",
    "@hey-api/sdk",
    "@tanstack/react-query",
  ],
});
