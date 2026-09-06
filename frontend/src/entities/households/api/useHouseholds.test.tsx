import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * Одиннадцатый и последний хук слоя `entities`
 * (см. `docs/reports/testing/frontend_coverage.md`).
 *
 * 🔴 **Здесь `enabled` — не оптимизация, а право доступа.** Список приглашений
 * бэкенд отдаёт только владельцу и отвечает 403 остальным. Запрашивать заведомо
 * запрещённое значит показывать участнику ошибку там, где у него просто нет
 * такого права: экран «сломан» вместо «этого раздела у вас нет».
 *
 * 🔴 **Ключи кэша здесь параметризованы id** (`["households", id, "members"]`),
 * и это единственное место в слое, где так. Общий префикс `["households"]`
 * в инвалидации накрывает и списки участников, и приглашения всех семей —
 * замена на точный ключ оставила бы соседние экраны со старыми данными.
 */

const listHouseholds = vi.fn();
const createHousehold = vi.fn();
const deleteHousehold = vi.fn();
const listMembers = vi.fn();
const removeMember = vi.fn();
const leaveHousehold = vi.fn();
const listInvites = vi.fn();
const createInvite = vi.fn();
const revokeInvite = vi.fn();
const acceptInvite = vi.fn();

vi.mock("@shared/api/generated", () => ({
  listHouseholdsEndpointApiHouseholdsGet: (...a: unknown[]) => listHouseholds(...a),
  createHouseholdEndpointApiHouseholdsPost: (...a: unknown[]) => createHousehold(...a),
  deleteHouseholdEndpointApiHouseholdsHouseholdIdDelete: (...a: unknown[]) => deleteHousehold(...a),
  listMembersEndpointApiHouseholdsHouseholdIdMembersGet: (...a: unknown[]) => listMembers(...a),
  removeMemberEndpointApiHouseholdsHouseholdIdMembersMemberUserIdDelete: (...a: unknown[]) =>
    removeMember(...a),
  leaveHouseholdEndpointApiHouseholdsHouseholdIdLeavePost: (...a: unknown[]) =>
    leaveHousehold(...a),
  listInvitesEndpointApiHouseholdsHouseholdIdInvitesGet: (...a: unknown[]) => listInvites(...a),
  createInviteEndpointApiHouseholdsHouseholdIdInvitesPost: (...a: unknown[]) => createInvite(...a),
  revokeInviteEndpointApiHouseholdsHouseholdIdInvitesInviteIdRevokePost: (...a: unknown[]) =>
    revokeInvite(...a),
  acceptInviteEndpointApiHouseholdsInvitesTokenAcceptPost: (...a: unknown[]) => acceptInvite(...a),
}));

const {
  useHouseholds,
  useHouseholdMembers,
  useHouseholdInvites,
  useCreateHousehold,
  useCreateInvite,
  useRevokeInvite,
  useRemoveMember,
  useLeaveHousehold,
  useDisbandHousehold,
  useAcceptInvite,
} = await import("./useHouseholds");

const ALL_KEY = { queryKey: ["households"] };

function makeWrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return { client, wrapper };
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("Чтение — пустой ответ не роняет экран", () => {
  it("список семей приходит массивом даже при пустом теле", async () => {
    /* `data ?? []` — потребители зовут `.map` сразу. У человека без семьи это
       обычное состояние, а не ошибка, и экран обязан показать приглашение
       завести семью, а не падать. */
    listHouseholds.mockResolvedValue({ data: undefined });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useHouseholds(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual([]);
  });
});

describe("🔴 `enabled` защищает от заведомо запрещённых запросов", () => {
  it("участники не запрашиваются без выбранной семьи", async () => {
    const { wrapper } = makeWrapper();
    renderHook(() => useHouseholdMembers(null), { wrapper });

    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(listMembers).not.toHaveBeenCalled();
  });

  it("приглашения НЕ запрашиваются у не-владельца, хотя семья выбрана", async () => {
    /* Главная проверка группы. Бэкенд отвечает 403 всем, кроме владельца.
       Сходить и получить отказ значит нарисовать участнику ошибку вместо того,
       чтобы просто не показывать раздел. */
    const { wrapper } = makeWrapper();
    renderHook(() => useHouseholdInvites(7, false), { wrapper });

    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(listInvites).not.toHaveBeenCalled();
  });

  it("владельцу приглашения запрашиваются", async () => {
    /* Обратная сторона: запрет, срабатывающий всегда, спрятал бы раздел и от того,
       кому он предназначен. */
    listInvites.mockResolvedValue({ data: [{ id: 1, role: "member" }] });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useHouseholdInvites(7, true), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(listInvites).toHaveBeenCalledWith({
      path: { household_id: 7 },
      throwOnError: true,
    });
  });
});

describe("Приглашения — ссылка приходит один раз", () => {
  it("создание отдаёт токен и ссылку, которых нет в списке", async () => {
    /* 🔴 `invite_url` и `token` бэкенд возвращает ТОЛЬКО здесь: в списке
       приглашений он их сознательно не отдаёт, чтобы ссылка не утекала при
       повторном чтении. Значит показать её можно ровно один раз, и экран
       обязан это учитывать, а не обещать «скопировать позже». */
    createInvite.mockResolvedValue({
      data: { id: 5, token: "tok", invite_url: "https://finpilot.ru/join?token=tok" },
    });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useCreateInvite(), { wrapper });
    result.current.mutate({ householdId: 7, email: "brother@test.io", role: "member" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(createInvite).toHaveBeenCalledWith({
      path: { household_id: 7 },
      body: { email: "brother@test.io", role: "member" },
      throwOnError: true,
    });
    expect(result.current.data).toMatchObject({ token: "tok" });
    expect(invalidate).toHaveBeenCalledWith(ALL_KEY);
  });

  it("приглашение без адреса — ссылку передают из рук в руки", async () => {
    /* Почта необязательна: человек может отправить ссылку в мессенджере.
       `email ?? null` здесь и превращает «поле не заполнено» в явный null. */
    createInvite.mockResolvedValue({ data: { id: 6, token: "t2" } });
    const { wrapper } = makeWrapper();

    const { result } = renderHook(() => useCreateInvite(), { wrapper });
    result.current.mutate({ householdId: 7, role: "viewer" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(createInvite).toHaveBeenCalledWith({
      path: { household_id: 7 },
      body: { email: null, role: "viewer" },
      throwOnError: true,
    });
  });

  it("отзыв приглашения кладёт ОБА id в путь", async () => {
    revokeInvite.mockResolvedValue({ data: null });
    const { wrapper } = makeWrapper();

    const { result } = renderHook(() => useRevokeInvite(), { wrapper });
    result.current.mutate({ householdId: 7, inviteId: 5 });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(revokeInvite).toHaveBeenCalledWith({
      path: { household_id: 7, invite_id: 5 },
      throwOnError: true,
    });
  });

  it("вход по ссылке обновляет список семей", async () => {
    acceptInvite.mockResolvedValue({ data: { household_id: 7, role: "member" } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useAcceptInvite(), { wrapper });
    result.current.mutate("tok");

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(acceptInvite).toHaveBeenCalledWith({ path: { token: "tok" }, throwOnError: true });
    expect(invalidate).toHaveBeenCalledWith(ALL_KEY);
  });
});

describe("Состав семьи — все мутации сбрасывают общий префикс", () => {
  it("создание семьи", async () => {
    createHousehold.mockResolvedValue({ data: { id: 8, name: "Семья" } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useCreateHousehold(), { wrapper });
    result.current.mutate("Семья");

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(createHousehold).toHaveBeenCalledWith({
      body: { name: "Семья" },
      throwOnError: true,
    });
    expect(invalidate).toHaveBeenCalledWith(ALL_KEY);
  });

  it("🔴 исключение участника сбрасывает ПРЕФИКС, а не список семей", async () => {
    /* Ключи здесь параметризованы id: `["households", 7, "members"]`. Общий префикс
       `["households"]` накрывает и его, и приглашения; точный ключ списка семей
       оставил бы открытый экран участников со старым составом — человек увидел бы
       в семье того, кого только что исключил. */
    removeMember.mockResolvedValue({ data: null });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useRemoveMember(), { wrapper });
    result.current.mutate({ householdId: 7, userId: "u-42" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(removeMember).toHaveBeenCalledWith({
      path: { household_id: 7, member_user_id: "u-42" },
      throwOnError: true,
    });
    expect(invalidate).toHaveBeenCalledWith(ALL_KEY);
  });

  it("выход из семьи и роспуск — разные эндпоинты, один ключ", async () => {
    /* Выход и роспуск легко спутать: у владельца на экране обе кнопки. Первый
       убирает из семьи только меня, второй уничтожает семью для всех. */
    leaveHousehold.mockResolvedValue({ data: null });
    deleteHousehold.mockResolvedValue({ data: null });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const leave = renderHook(() => useLeaveHousehold(), { wrapper });
    leave.result.current.mutate(7);
    await waitFor(() => expect(leave.result.current.isSuccess).toBe(true));
    expect(leaveHousehold).toHaveBeenCalledWith({
      path: { household_id: 7 },
      throwOnError: true,
    });

    const disband = renderHook(() => useDisbandHousehold(), { wrapper });
    disband.result.current.mutate(7);
    await waitFor(() => expect(disband.result.current.isSuccess).toBe(true));
    expect(deleteHousehold).toHaveBeenCalledWith({
      path: { household_id: 7 },
      throwOnError: true,
    });

    expect(invalidate).toHaveBeenCalledTimes(2);
    expect(invalidate).toHaveBeenCalledWith(ALL_KEY);
  });
});
