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
  },
});
