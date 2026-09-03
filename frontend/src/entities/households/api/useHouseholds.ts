import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  listHouseholdsEndpointApiHouseholdsGet,
  createHouseholdEndpointApiHouseholdsPost,
  deleteHouseholdEndpointApiHouseholdsHouseholdIdDelete,
  listMembersEndpointApiHouseholdsHouseholdIdMembersGet,
  removeMemberEndpointApiHouseholdsHouseholdIdMembersMemberUserIdDelete,
  leaveHouseholdEndpointApiHouseholdsHouseholdIdLeavePost,
  listInvitesEndpointApiHouseholdsHouseholdIdInvitesGet,
  createInviteEndpointApiHouseholdsHouseholdIdInvitesPost,
  revokeInviteEndpointApiHouseholdsHouseholdIdInvitesInviteIdRevokePost,
  acceptInviteEndpointApiHouseholdsInvitesTokenAcceptPost,
} from "@shared/api/generated";
import type {
  HouseholdResponse,
  HouseholdMemberResponse,
  HouseholdInviteResponse,
  InviteAcceptResponse,
} from "../model/types";

const HOUSEHOLDS_KEY = ["households"];
const membersKey = (id: number) => ["households", id, "members"];
const invitesKey = (id: number) => ["households", id, "invites"];

/** GET /api/households — семьи, в которых я состою, с моей ролью и числом участников. */
export function useHouseholds() {
  return useQuery({
    queryKey: HOUSEHOLDS_KEY,
    queryFn: async () => {
      const { data } = await listHouseholdsEndpointApiHouseholdsGet({ throwOnError: true });
      return (data ?? []) as HouseholdResponse[];
    },
  });
}

/** GET /api/households/{id}/members — только для участников, чужим 403. */
export function useHouseholdMembers(householdId: number | null) {
  return useQuery({
    queryKey: householdId === null ? ["households", "members", "none"] : membersKey(householdId),
    enabled: householdId !== null,
    queryFn: async () => {
      const { data } = await listMembersEndpointApiHouseholdsHouseholdIdMembersGet({
        path: { household_id: householdId as number },
        throwOnError: true,
      });
      return (data ?? []) as HouseholdMemberResponse[];
    },
  });
}

/**
 * GET /api/households/{id}/invites — только владельцу (бэкенд отвечает 403 остальным).
 *
 * `enabled` учитывает роль, а не только наличие id: запрашивать заведомо запрещённое
 * значит показывать участнику ошибку там, где у него просто нет такого права.
 */
export function useHouseholdInvites(householdId: number | null, isOwner: boolean) {
  return useQuery({
    queryKey: householdId === null ? ["households", "invites", "none"] : invitesKey(householdId),
    enabled: householdId !== null && isOwner,
    queryFn: async () => {
      const { data } = await listInvitesEndpointApiHouseholdsHouseholdIdInvitesGet({
        path: { household_id: householdId as number },
        throwOnError: true,
      });
      return (data ?? []) as HouseholdInviteResponse[];
    },
  });
}

function useInvalidateAll() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: HOUSEHOLDS_KEY });
}

export function useCreateHousehold() {
  const invalidate = useInvalidateAll();
  return useMutation({
    mutationFn: async (name: string) => {
      const { data } = await createHouseholdEndpointApiHouseholdsPost({
        body: { name },
        throwOnError: true,
      });
      return data as HouseholdResponse;
    },
    onSuccess: invalidate,
  });
}

/**
 * POST /api/households/{id}/invites — создаёт приглашение и ВОЗВРАЩАЕТ ссылку.
 *
 * `invite_url` и `token` приходят только здесь: в списке приглашений бэкенд их
 * сознательно не отдаёт (`routes_households.py`), чтобы ссылка не утекала при
 * повторном чтении. Значит показать её пользователю можно ровно один раз —
 * и экран обязан это учитывать, а не предлагать «скопировать позже».
 */
export function useCreateInvite() {
  const invalidate = useInvalidateAll();
  return useMutation({
    mutationFn: async (args: { householdId: number; email?: string | null; role: string }) => {
      const { data } = await createInviteEndpointApiHouseholdsHouseholdIdInvitesPost({
        path: { household_id: args.householdId },
        body: { email: args.email ?? null, role: args.role as "member" | "viewer" },
        throwOnError: true,
      });
      return data as HouseholdInviteResponse;
    },
    onSuccess: invalidate,
  });
}

export function useRevokeInvite() {
  const invalidate = useInvalidateAll();
  return useMutation({
    mutationFn: async (args: { householdId: number; inviteId: number }) => {
      const { data } = await revokeInviteEndpointApiHouseholdsHouseholdIdInvitesInviteIdRevokePost(
        {
          path: { household_id: args.householdId, invite_id: args.inviteId },
          throwOnError: true,
        },
      );
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useRemoveMember() {
  const invalidate = useInvalidateAll();
  return useMutation({
    mutationFn: async (args: { householdId: number; userId: string }) => {
      const { data } =
        await removeMemberEndpointApiHouseholdsHouseholdIdMembersMemberUserIdDelete({
          path: { household_id: args.householdId, member_user_id: args.userId },
          throwOnError: true,
        });
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useLeaveHousehold() {
  const invalidate = useInvalidateAll();
  return useMutation({
    mutationFn: async (householdId: number) => {
      const { data } = await leaveHouseholdEndpointApiHouseholdsHouseholdIdLeavePost({
        path: { household_id: householdId },
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}

export function useDisbandHousehold() {
  const invalidate = useInvalidateAll();
  return useMutation({
    mutationFn: async (householdId: number) => {
      const { data } = await deleteHouseholdEndpointApiHouseholdsHouseholdIdDelete({
        path: { household_id: householdId },
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}

/** POST /api/households/invites/{token}/accept — вход по ссылке приглашения. */
export function useAcceptInvite() {
  const invalidate = useInvalidateAll();
  return useMutation({
    mutationFn: async (token: string) => {
      const { data } = await acceptInviteEndpointApiHouseholdsInvitesTokenAcceptPost({
        path: { token },
        throwOnError: true,
      });
      return data as InviteAcceptResponse;
    },
    onSuccess: invalidate,
  });
}
