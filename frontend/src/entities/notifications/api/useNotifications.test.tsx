import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * Седьмой хук слоя `entities` (см. `docs/reports/testing/frontend_coverage.md`).
 *
 * 🔴 **Здесь единственная во всём слое политика ретрая — и она защищает продукт
 * от самого себя.** Колокольчик стоит в топбаре на КАЖДОМ экране. При отозванном
 * согласии `/api/notifications/*` отвечает 403 (`_FIN`, v8.32.0), и обычный ретрай
 * дал бы **три отказа на каждой странице** — то есть человек, отозвавший согласие,
 * получал бы шквал запросов вместо тишины.
 *
 * 🔴 **Политика опиралась на `error.status`, которого до v9.1.0 НЕ СУЩЕСТВОВАЛО.**
 * Сгенерированный клиент бросал только тело ответа, код терялся, и проверка
 * `status === 403` всегда давала false: докстрока обещала «не ретраим отказ»,
 * а код ретраил. Дефект нашло `/code-review`, и заметить его глазами было нельзя —
 * докстрока и реализация выглядели согласованными.
 *
 * Поэтому тесты ниже проверяют **число вызовов**, а не только результат: именно
 * счётчик отличает «не ретраит» от «ретраит и всё равно падает».
 */

const feed = vi.fn();
const unreadCount = vi.fn();
const markRead = vi.fn();
const markAllRead = vi.fn();

vi.mock("@shared/api/generated", () => ({
  notificationsFeedApiNotificationsFeedGet: (...a: unknown[]) => feed(...a),
  notificationsUnreadCountApiNotificationsUnreadCountGet: (...a: unknown[]) => unreadCount(...a),
  notificationMarkReadApiNotificationsNotificationIdReadPost: (...a: unknown[]) => markRead(...a),
  notificationsMarkAllReadApiNotificationsReadAllPost: (...a: unknown[]) => markAllRead(...a),
}));

const { useNotificationsFeed, useUnreadCount, useMarkRead, useMarkAllRead } =
  await import("./useNotifications");

const FEED_KEY = { queryKey: ["notifications", "feed"] };
const UNREAD_KEY = { queryKey: ["notifications", "unread-count"] };

function makeWrapper() {
  /* 🔴 Ретрай НЕ отключается в клиенте: политика живёт в самих хуках, и подменять
     её здесь значило бы проверять настройку теста вместо кода. Мутации — отдельно,
     им ретрай не нужен и он только замедлил бы проверку. */
  const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return { client, wrapper };
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("useUnreadCount — бейдж на каждом экране", () => {
  it("разворачивает ответ до числа", async () => {
    unreadCount.mockResolvedValue({ data: { unread_count: 3 } });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useUnreadCount(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toBe(3);
  });

  it("🔴 не повторяет запрос ни разу — ни на 403, ни на любой другой ошибке", async () => {
    /* `retry: false` здесь не экономия, а необходимость: колокольчик на каждом экране,
       и три повтора превратились бы в три отказа на каждой странице продукта. */
    unreadCount.mockRejectedValue({ detail: "Требуется согласие.", status: 403 });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useUnreadCount(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(unreadCount).toHaveBeenCalledTimes(1);
  });
});

describe("useNotificationsFeed — лента открытой панели", () => {
  it("не запрашивается, пока панель закрыта", async () => {
    /* `enabled` — не оптимизация: лента тяжелее счётчика, и тянуть её ради бейджа
       значит платить полным ответом за одно число. */
    const { wrapper } = makeWrapper();
    renderHook(() => useNotificationsFeed(false), { wrapper });

    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(feed).not.toHaveBeenCalled();
  });

  it("🔴 отказ согласия не повторяется: 403 — осознанный ответ, а не сбой связи", async () => {
    feed.mockRejectedValue({ detail: "Требуется согласие.", status: 403 });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useNotificationsFeed(true), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(feed).toHaveBeenCalledTimes(1);
  });

  it("🔴 истёкшая сессия тоже не повторяется", async () => {
    /* 401 повторять бессмысленно по той же причине: токен не станет действительным
       от третьей попытки. Человеку нужна `SessionExpiredPanel`, а не ожидание. */
    feed.mockRejectedValue({ detail: "Требуется аутентификация.", status: 401 });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useNotificationsFeed(true), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(feed).toHaveBeenCalledTimes(1);
  });

  it("а вот сетевой сбой повторяется — связь могла восстановиться", async () => {
    /* Обратная сторона: политика, не повторяющая ничего, лишила бы ленту
       единственного случая, где повтор осмыслен. */
    feed.mockRejectedValue(new TypeError("Failed to fetch"));
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useNotificationsFeed(true), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true), { timeout: 5000 });
    expect(feed.mock.calls.length).toBeGreaterThan(1);
  });
});

describe("Отметки о прочтении обновляют И ленту, И бейдж", () => {
  it("отметка одной новости трогает оба ключа", async () => {
    /* 🔴 Инвалидировать только ленту значит оставить бейдж со старым числом,
       пока панель открыта: список и счётчик над ним разошлись бы на глазах. */
    markRead.mockResolvedValue({ data: { id: 4 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useMarkRead(), { wrapper });
    result.current.mutate(4);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(markRead).toHaveBeenCalledWith({
      path: { notification_id: 4 },
      throwOnError: true,
    });
    expect(invalidate).toHaveBeenCalledWith(FEED_KEY);
    expect(invalidate).toHaveBeenCalledWith(UNREAD_KEY);
  });

  it("«прочитать всё» тоже трогает оба ключа", async () => {
    markAllRead.mockResolvedValue({ data: { updated: 7 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useMarkAllRead(), { wrapper });
    result.current.mutate();

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(invalidate).toHaveBeenCalledWith(FEED_KEY);
    expect(invalidate).toHaveBeenCalledWith(UNREAD_KEY);
  });
});
