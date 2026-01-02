import { api } from "./client";
import type { League, FantasyTeam, DailyStandings, AgentTask, Player } from "../types";

export interface CreateLeagueRequest {
  name: string;
  season?: string;
  espn_league_id?: number;
  espn_s2?: string;
  espn_swid?: string;
}

export interface CreateTeamRequest {
  name: string;
  owner_name?: string;
  league_id?: number;
}

export interface ESPNConfigRequest {
  espn_league_id: number;
  espn_s2: string;
  espn_swid: string;
}

/**
 * League and Team API endpoints
 */
export const leaguesApi = {
  // League endpoints
  async getLeagues(): Promise<League[]> {
    return api.get<League[]>("/leagues");
  },

  async createLeague(data: CreateLeagueRequest): Promise<League> {
    return api.post<League>("/leagues", data);
  },

  async getStandings(leagueId: number): Promise<DailyStandings[]> {
    return api.get<DailyStandings[]>(`/leagues/${leagueId}/standings`);
  },

  async configureESPN(leagueId: number, config: ESPNConfigRequest): Promise<{ message: string }> {
    return api.post(`/leagues/${leagueId}/configure_espn`, config);
  },

  async getESPNStatus(leagueId: number): Promise<{
    espn_configured: boolean;
    espn_league_id?: number;
    last_sync?: string;
    credentials_set: boolean;
  }> {
    return api.get(`/leagues/${leagueId}/espn_status`);
  },

  // Team endpoints
  async getTeams(): Promise<FantasyTeam[]> {
    return api.get<FantasyTeam[]>("/teams");
  },

  async getTeam(teamId: number): Promise<FantasyTeam> {
    return api.get<FantasyTeam>(`/teams/${teamId}`);
  },

  async createTeam(data: CreateTeamRequest): Promise<FantasyTeam> {
    return api.post<FantasyTeam>("/teams", data);
  },

  async getTeamPlayers(teamId: number): Promise<Player[]> {
    return api.get<Player[]>(`/teams/${teamId}/players`);
  },

  async addPlayerToTeam(teamId: number, playerId: number): Promise<{ message: string }> {
    return api.post(`/teams/${teamId}/add_player`, { player_id: playerId });
  },

  // Task endpoints
  async getTask(taskId: string): Promise<AgentTask> {
    return api.get<AgentTask>(`/tasks/${taskId}`);
  },

  async triggerIngestion(days = 15, mock = false): Promise<{ task_id: string; status: string }> {
    return api.post("/ingest", { days, mock });
  },

  async triggerHybridSync(
    leagueId: number,
    options?: {
      sync_nba_players?: boolean;
      sync_nba_stats?: boolean;
      sync_espn_rosters?: boolean;
      limit_nba_players?: number;
      mock_nba?: boolean;
    }
  ): Promise<{ task_id: string; status: string }> {
    return api.post(`/leagues/${leagueId}/hybrid_sync`, options || {});
  },
};
