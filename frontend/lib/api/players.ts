import { api } from "./client";
import type { Player, PlayerStats } from "../types";

export interface GetPlayersParams {
  active_only?: boolean;
  limit?: number;
  offset?: number;
}

/**
 * Player API endpoints
 */
export const playersApi = {
  /**
   * Get all players with optional filtering
   */
  async getPlayers(params?: GetPlayersParams): Promise<Player[]> {
    return api.get<Player[]>("/players", { params });
  },

  /**
   * Get a single player by ID
   */
  async getPlayer(id: number): Promise<Player> {
    return api.get<Player>(`/players/${id}`);
  },

  /**
   * Get all player stats with Z-scores
   */
  async getStats(): Promise<PlayerStats[]> {
    return api.get<PlayerStats[]>("/stats");
  },

  /**
   * Search players by name
   */
  async searchPlayers(query: string, limit = 10): Promise<Player[]> {
    const players = await this.getPlayers({ limit: 500 });
    const lowerQuery = query.toLowerCase();
    return players
      .filter((p) => p.full_name.toLowerCase().includes(lowerQuery))
      .slice(0, limit);
  },
};
