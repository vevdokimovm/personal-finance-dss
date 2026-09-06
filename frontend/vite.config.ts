/// <reference types="vitest/config" />
import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { tanstackRouter } from "@tanstack/router-plugin/vite";

// Dev-прокси /api -> FastAPI (127.0.0.1:8000), см. docs/frontend_migration_plan.md §1.5.
// Прод: /dist раздаёт nginx, /api идёт на FastAPI напрямую — здесь прокси не нужен.
export default defineConfig({
  plugins: [
    tanstackRouter({ target: "react", autoCodeSplitting: true, routesDirectory: "./src/routes" }),
    react(),
  ],
  resolve: {
    alias: {
      "@app": path.resolve(import.meta.dirname, "./src/app"),
      "@pages": path.resolve(import.meta.dirname, "./src/pages"),
      "@widgets": path.resolve(import.meta.dirname, "./src/widgets"),
      "@features": path.resolve(import.meta.dirname, "./src/features"),
      "@entities": path.resolve(import.meta.dirname, "./src/entities"),
      "@shared": path.resolve(import.meta.dirname, "./src/shared"),
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/shared/lib/test/setup.ts"],
    exclude: ["**/node_modules/**", "**/e2e/**"],
    coverage: {
      provider: "v8",
      /* `json` даёт покрытие ПОСТРОЧНО (`coverage-final.json`) — без него непокрытые
         строки приходится угадывать по HTML, а его нумерация со строками файла
         не совпадает. Сводка отвечает «сколько», этот отчёт — «где именно». */
      reporter: ["text-summary", "json-summary", "json", "html"],
      reportsDirectory: "./coverage",
      include: ["src/**/*.{ts,tsx}"],
      /* Что исключено и почему — важнее самого числа: покрытие, посчитанное
         по сгенерированному клиенту и точкам входа, измеряет генератор,
         а не написанные нами тесты. */
      exclude: [
        "src/shared/api/generated/**",  // артефакт hey-api, не наш код
        "src/**/*.test.{ts,tsx}",
        "src/**/*.d.ts",
        "src/main.tsx",                 // точка входа: монтирует и всё
        "src/vite-env.d.ts",
        "src/routeTree.gen.ts",         // артефакт TanStack Router
      ],
      /* 🔴 Тот же порог, что у бэкенда (`.coveragerc: fail_under = 90`).
         Решение владельца 06.09.2026, дословно: «тогда для бэкенда точно такие же
         требования как и для фронта покрытие должно быть больше или равно 90%».

         Порог поставлен СРАЗУ на 90, а не «по текущему уровню с постепенным подъёмом».
         Ступенчатый порог удобен и нечестен: он всегда зелёный, то есть не сообщает
         ничего, а цифра в нём описывает прошлое, а не требование. Красный гейт при
         80.8 % говорит правду — до планки девять пунктов.

         🔴 Список `exclude` выше НЕ пополняется ради процента. Покрытие, которое
         регулируется тем, что из него вычеркнули, измеряет длину списка исключений. */
      thresholds: {
        lines: 90,
        statements: 90,
        functions: 90,
        branches: 90,
      },
    },
  },
});
