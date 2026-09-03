import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  notificationsFeedApiNotificationsFeedGet,
  notificationsUnreadCountApiNotificationsUnreadCountGet,
  notificationMarkReadApiNotificationsNotificationIdReadPost,
  notificationsMarkAllReadApiNotificationsReadAllPost,
} from "@shared/api/generated";
import type { NotificationFeed } from "../model/types";

const FEED_KEY = ["notifications", "feed"];
const UNREAD_KEY = ["notifications", "unread-count"];

/** GET /api/notifications/feed — лента + счётчик одним ответом (`NotificationFeed`).
 *
 * Лента и счётчик приходят вместе сознательно: бейдж колокольчика и содержимое панели
 * обязаны показывать одно и то же число. Отдельный запрос счётчика существует для
 * случая, когда панель ЗАКРЫТА (см. `useUnreadCount`) — тогда тянуть всю ленту незачем. */
export function useNotificationsFeed(enabled: boolean) {
  return useQuery({
    queryKey: FEED_KEY,
    enabled,
    queryFn: async () => {
      const { data } = await notificationsFeedApiNotificationsFeedGet({ throwOnError: true });
      return data as NotificationFeed;
    },
  });
}

/** GET /api/notifications/unread-count — только бейдж, пока панель закрыта.
 *
 * `retry: false` здесь не экономия, а необходимость: колокольчик стоит в топбаре на
 * КАЖДОМ экране, и при отозванном согласии эндпоинт отвечает 403 (`_FIN`, v8.32.0).
 * С обычным ретраем это дало бы три отказа на каждой странице продукта. */
export function useUnreadCount() {
  return useQuery({
    queryKey: UNREAD_KEY,
    retry: false,
    queryFn: async () => {
      const { data } = await notificationsUnreadCountApiNotificationsUnreadCountGet({
        throwOnError: true,
      });
      return (data as { unread_count: number }).unread_count;
    },
  });
}

function useInvalidateNotifications() {
  const queryClient = useQueryClient();
  return () => {
    queryClient.invalidateQueries({ queryKey: FEED_KEY });
    queryClient.invalidateQueries({ queryKey: UNREAD_KEY });
  };
}

/** POST /api/notifications/{id}/read — инвалидируем ОБА ключа: иначе бейдж остался бы
 * со старым числом, пока панель открыта, и разошёлся бы со списком под ним. */
export function useMarkRead() {
  const invalidate = useInvalidateNotifications();
  return useMutation({
    mutationFn: async (notificationId: number) => {
      const { data } = await notificationMarkReadApiNotificationsNotificationIdReadPost({
        path: { notification_id: notificationId },
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}

/** POST /api/notifications/read-all */
export function useMarkAllRead() {
  const invalidate = useInvalidateNotifications();
  return useMutation({
    mutationFn: async () => {
      const { data } = await notificationsMarkAllReadApiNotificationsReadAllPost({
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}
