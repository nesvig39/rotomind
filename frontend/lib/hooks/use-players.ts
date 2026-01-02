import { useQuery } from "@tanstack/react-query";
import { playersApi, type GetPlayersParams } from "../api/players";

/**
 * Hook to fetch all players
 */
export function usePlayers(params?: GetPlayersParams) {
  return useQuery({
    queryKey: ["players", params],
    queryFn: () => playersApi.getPlayers(params),
  });
}

/**
 * Hook to fetch a single player
 */
export function usePlayer(playerId: number) {
  return useQuery({
    queryKey: ["player", playerId],
    queryFn: () => playersApi.getPlayer(playerId),
    enabled: !!playerId,
  });
}

/**
 * Hook to fetch player stats with Z-scores
 */
export function usePlayerStats() {
  return useQuery({
    queryKey: ["stats"],
    queryFn: () => playersApi.getStats(),
  });
}
