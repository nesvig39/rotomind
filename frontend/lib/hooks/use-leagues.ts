import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { leaguesApi, type CreateLeagueRequest, type CreateTeamRequest } from "../api/leagues";

/**
 * Hook to fetch all leagues
 */
export function useLeagues() {
  return useQuery({
    queryKey: ["leagues"],
    queryFn: () => leaguesApi.getLeagues(),
  });
}

/**
 * Hook to fetch standings for a league
 */
export function useStandings(leagueId: number | null) {
  return useQuery({
    queryKey: ["standings", leagueId],
    queryFn: () => leaguesApi.getStandings(leagueId!),
    enabled: !!leagueId,
  });
}

/**
 * Hook to fetch all teams
 */
export function useTeams() {
  return useQuery({
    queryKey: ["teams"],
    queryFn: () => leaguesApi.getTeams(),
  });
}

/**
 * Hook to fetch a single team
 */
export function useTeam(teamId: number | null) {
  return useQuery({
    queryKey: ["team", teamId],
    queryFn: () => leaguesApi.getTeam(teamId!),
    enabled: !!teamId,
  });
}

/**
 * Hook to fetch team players
 */
export function useTeamPlayers(teamId: number | null) {
  return useQuery({
    queryKey: ["team-players", teamId],
    queryFn: () => leaguesApi.getTeamPlayers(teamId!),
    enabled: !!teamId,
  });
}

/**
 * Hook to create a new league
 */
export function useCreateLeague() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateLeagueRequest) => leaguesApi.createLeague(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leagues"] });
    },
  });
}

/**
 * Hook to create a new team
 */
export function useCreateTeam() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateTeamRequest) => leaguesApi.createTeam(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["teams"] });
    },
  });
}

/**
 * Hook to trigger data ingestion
 */
export function useIngestion() {
  return useMutation({
    mutationFn: ({ days, mock }: { days?: number; mock?: boolean }) =>
      leaguesApi.triggerIngestion(days, mock),
  });
}
